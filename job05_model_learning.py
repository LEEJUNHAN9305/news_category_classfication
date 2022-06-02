import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import *
from tensorflow.keras.layers import *
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" #CPU를 쓰도록 강제. GPU 사용 시 지우면 됨

#train, test set split
X_train, X_test, Y_train, Y_test = np.load('./crawling_data/news_data_max_17_wordsize_12426.npy', allow_pickle=True)
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)

#modeling
model = Sequential()
model.add(Embedding(12426, 300, input_length=17))
          #embedding layer 제작 -> 단어의 의미를 학습
          #12426차원 -> 300 축소차원으로 줄임. 데이터의 희소성을 방지
model.add(Conv1D(32, kernel_size=5, padding='same', activation='relu'))
model.add(MaxPool1D(pool_size=1))
                    #pooling 안함
model.add(LSTM(128, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh'))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(6, activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
fit_hist = model.fit(X_train, Y_train, batch_size=128, epochs=10, validation_data=(X_test, Y_test))
model.save('./models/news_category_classification_model_{}.h5'.format(fit_hist.history['val_accuracy'][-1]))
plt.plot(fit_hist.history['val_accuracy'], label = 'val_accuracy')
plt.plot(fit_hist.history['accuracy'], label = 'accuracy')
plt.legend()
plt.show()