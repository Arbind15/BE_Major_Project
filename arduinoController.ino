int enA = 10;
int in1 = 9;
int in2 = 8;
int enB = 5;
int in3 = 7;
int in4 = 6;
int speedA=0;
int speedB=0;
int B_INTR=2;

void setup() {
  Serial.begin(9600);
  pinMode(enA, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  analogWrite(enA, speedA);
  analogWrite(enB, speedB);
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  pinMode(B_INTR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(B_INTR), InterruptBrake, CHANGE);
}

void loop() {
    String recvString = Serial.readString();
    int i1 = recvString.indexOf(',');
    int i2 = recvString.indexOf(',', i1+1);
    int i3 = recvString.indexOf(',', i2+1);
    int sA = recvString.substring(0, i1).toInt();
    int sB = recvString.substring(i1 + 1,i2).toInt();
    int dir = recvString.substring(i2 + 1).toInt();
    if(sA<=200 && sB<=200){
      if(dir==2){
        digitalWrite(in1, HIGH);
        digitalWrite(in2, LOW);
        digitalWrite(in3, LOW);
        digitalWrite(in4, HIGH);
        analogWrite(enA, sA);
        analogWrite(enB, sB);
        delay(100);
        analogWrite(enA, 0);
        analogWrite(enB, 0);
      }
      else if(dir==3){
        digitalWrite(in1, LOW);
        digitalWrite(in2, HIGH);
        digitalWrite(in3, HIGH);
        digitalWrite(in4, LOW);
        analogWrite(enA, sA);
        analogWrite(enB, sB);
        delay(100);
        analogWrite(enA, 0);
        analogWrite(enB, 0);
      }
      else if(dir==1){
        digitalWrite(in1, LOW);
        digitalWrite(in2, HIGH);
        digitalWrite(in3, LOW);
        digitalWrite(in4, HIGH);
        analogWrite(enA, sA);
        analogWrite(enB, sB);
        delay(300);
        analogWrite(enA, 0);
        analogWrite(enB, 0);
      }
    }
    sA=0;
    sB=0;
    Serial.write(1);
}

void InterruptBrake() {
  int INTR_Value = digitalRead(B_INTR);
  analogWrite(enA, 0);
  analogWrite(enB, 0);
  Serial.write(1);
  while(INTR_Value==HIGH){
    INTR_Value = digitalRead(B_INTR);
    }
  __asm__ __volatile__("jmp 0");
}