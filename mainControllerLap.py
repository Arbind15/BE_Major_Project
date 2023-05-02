import socket
import numpy as np
import cv2, threading
import imagezmq
import urllib.request
import tarfile
import os
import tensorflow as tf

image_hub = imagezmq.ImageHub()
cur_diff = None
# Bind the socket to the IP address and port
laptop_ip = ""
laptop_port = 65432
confidence_threshold=0.5
# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((laptop_ip, laptop_port))
# Listen for incoming connections
sock.listen(1)
# Accept the incoming connection
conn, addr = sock.accept()
baseSpeed = 80  #make sure to check upper limit in arduino program!
offset = 60
# Download pre-trained model from TensorFlow Model Zoo
MODEL_NAME = 'ssd_mobilenet_v2_coco_2018_03_29'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
DOWNLOAD_URL = DOWNLOAD_BASE + MODEL_FILE
DEST_DIR = 'models/'

if not os.path.exists(DEST_DIR):
    os.makedirs(DEST_DIR)

if not os.path.exists(os.path.join(DEST_DIR, MODEL_NAME)):
    urllib.request.urlretrieve(DOWNLOAD_URL, os.path.join(DEST_DIR, MODEL_FILE))
    tar_file = tarfile.open(os.path.join(DEST_DIR, MODEL_FILE))
    tar_file.extractall(DEST_DIR)
    tar_file.close()

# Load model
PATH_TO_CKPT = os.path.join(DEST_DIR, MODEL_NAME, 'frozen_inference_graph.pb')
PATH_TO_LABELS = os.path.join(DEST_DIR, 'data', 'mscoco_label_map.pbtxt')
NUM_CLASSES = 90

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.compat.v2.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# Load label map
label_map = {}
with open(PATH_TO_LABELS, 'r') as f:
    for line in f:
        if 'id:' in line:
            id = int(line.split(':')[-1])
        elif 'display_name:' in line:
            name = line.split(':')[-1].strip().strip('"')
            label_map[id] = name

def process(frame):
    global cur_diff
    height = frame.shape[0]
    width = frame.shape[1]
    gray_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    (thresh, im_bw) = cv2.threshold(gray_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    region_of_interest_vertices = [
        (0, 115),  # top left
        (width - 0, 115),  # top right
        (width - 0, height - 115),  # buttom right
        (0, height - 115)  # buttom left
    ]
    mask = np.zeros_like(im_bw)
    match_mask_color = 255  # only one color because it is a gray image
    cv2.fillPoly(mask, np.array([region_of_interest_vertices], np.int32), match_mask_color)
    masked_image = cv2.bitwise_and(im_bw, mask)
    # Find contours
    cnts = cv2.findContours(masked_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    # Iterate thorugh contours and draw rectangles around contours
    x_avg = 0
    f_rect = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        # print(w, h)
        if 10 < w < 40 and 10 < h < 20:
            f_rect.append(c)
            x_avg += x + (w / 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
    if len(f_rect) ==2:
        x_avg = int(x_avg / len(f_rect))
        cv2.line(frame, (x_avg, 115), (x_avg, height - 115), (0, 255, 0), thickness=3)
        cur_diff = int((width / 2) - x_avg)
    else:
        cur_diff = None
    frame = cv2.rectangle(frame, region_of_interest_vertices[0], region_of_interest_vertices[2],
                          (255, 0, 0), 2)
    cv2.line(frame, (int(width / 2), 115), (int(width / 2), height - 115), (0, 0, 255), thickness=2)
    return frame

with detection_graph.as_default():
    with tf.compat.v1.Session(graph=detection_graph) as sess:
        # Get input and output tensors
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        while True:
            rpi_name, frame = image_hub.recv_image()
            if (frame is not None):
                frame1 = np.copy(frame)
                frame = process(frame)

                # Resize image to match input size of model
                image = cv2.resize(frame1, (300, 300))
                # Expand dimensions of image tensor
                image_expanded = np.expand_dims(image, axis=0)
                # Run inference
                (boxes, scores, _, _) = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_expanded})
                # Filter out detections with confidence lower than threshold
                boxes = np.squeeze(boxes)
                scores = np.squeeze(scores)
                valid_indices = np.where(scores > confidence_threshold)[0]
                boxes = boxes[valid_indices]
                for i in range(len(valid_indices)):
                    box = boxes[i].tolist()
                    # Calculate coordinates of bounding box
                    ymin, xmin, ymax, xmax = box
                    im_height, im_width, _ = frame.shape
                    left = int(xmin * im_width)
                    top = int(ymin * im_height)
                    right = int(xmax * im_width)
                    bottom = int(ymax * im_height)
                    # Draw bounding box on image
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                cv2.imshow(rpi_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    conn.close()
                    break
                if cur_diff is not None and len(valid_indices) <= 0:
                    # 1->f, 2->r, 3->l, 4->s
                    # sA,sB,dir
                    if cur_diff < -10:
                        conn.send(
                            bytes(str(baseSpeed + offset) + "," + str(baseSpeed + offset) + ",2", 'utf-8'))  # right
                    elif cur_diff > 10:
                        conn.send(
                            bytes(str(baseSpeed + offset) + "," + str(baseSpeed + offset) + ",3", 'utf-8'))  # left
                    else:
                        conn.send(bytes(str(abs(baseSpeed)) + "," + str(abs(baseSpeed)) + ",1", 'utf-8'))  # forward
                else:
                    conn.send(bytes("0,0,4", 'utf-8'))  # stop
                # conn.send(bytes("2,50", 'utf-8'))
            else:
                break
            image_hub.send_reply(b'OK')

conn.close()
cv2.destroyAllWindows()