#include <Arduino.h>

#define S0 10
#define S1 11
#define S2 12
#define S3 13

#define M0 4
#define M1 5
#define M2 6
#define M3 7

#define O A0
#define E 8 // unused

int offset[15][15];

// 3V3: 630mA; GND: 580mA

const int muxDelayMicros = 10; // delay for the mux to settle; digitalWrite takes about 4 us, but analogRead takes 100 us
// time to measure whole board = 225 * measureTimes * muxDelayMicros (in microseconds)
const int blackStoneTreshold = 10; // treshold for black stone detection
const int whiteStoneTreshold = 10; // treshold for white stone detection

template<typename T>
struct Array2D {
  T values[15][15];

  // Allow shorthand: arr[i][j]
  T* operator[](size_t row) {
    return values[row];
  }
};

void setMuxI(int i) {
  // set individual mux
  digitalWrite(S0, (i & 1) ? HIGH : LOW);
  digitalWrite(S1, (i & 2) ? HIGH : LOW);
  digitalWrite(S2, (i & 4) ? HIGH : LOW);
  digitalWrite(S3, (i & 8) ? HIGH : LOW);
}

void setMuxJ(int j) {
  // set main mux
  digitalWrite(M0, (j & 1) ? HIGH : LOW);
  digitalWrite(M1, (j & 2) ? HIGH : LOW);
  digitalWrite(M2, (j & 4) ? HIGH : LOW);
  digitalWrite(M3, (j & 8) ? HIGH : LOW);
}

/**
 * Returns 2D array of stone values after one read
 */
Array2D<int> readStones() {
  Array2D<int> values;

  for (int i = 0; i < 15; i++) {
    // set individual mux
    setMuxI(i);

    for (int j = 0; j < 15; j++) {
      // set main mux
      setMuxJ(j);

      delayMicroseconds(muxDelayMicros);
      values[i][j] = analogRead(O);
    }
  }

  return values;
}

void calibrate() {
  // read stones and save values
  Array2D<int> values = readStones();
  for (int i = 0; i < 15; i++) {
    for (int j = 0; j < 15; j++) {
      offset[i][j] = values[i][j];
    }
  }
}

Array2D<char> getStoneColors(Array2D<int> input) {
  Array2D<char> result;

  for (int i = 0; i < 15; i++) {
    for (int j = 0; j < 15; j++) {
      if (input[i][j] - offset[i][j] > blackStoneTreshold) {
        result[i][j] = 'B'; // black stone
      } else if (input[i][j] - offset[i][j] < -whiteStoneTreshold) {
        result[i][j] = 'W'; // white stone
      } else {
        result[i][j] = ' '; // empty
      }
    }
  }

  return result;
}

template<typename T>
T rotateLeft(T value) {
  

  return value;
}

void setup() {
  Serial.begin(BAUDRATE);

  pinMode(A0, INPUT);
  pinMode(E, OUTPUT);
  digitalWrite(E, LOW);
  
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(M0, OUTPUT);
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);
  pinMode(M3, OUTPUT);

  calibrate();
}


void loop() {
  Array2D<int> values = readStones();
  Array2D<char> colors = getStoneColors(values);
  
  for (int i = 0; i < 15; i++) {
    for (int j = 0; j < 15; j++) {
      Serial.print("\t");
      Serial.print(colors[i][j]);
      Serial.print(" ");
    }
    Serial.println();
  }
  Serial.println();

  delay(100);
}

