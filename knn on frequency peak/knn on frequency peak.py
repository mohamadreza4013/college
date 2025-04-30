import os
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import librosa
import matplotlib.pyplot as plt

def extract_peak_frequency(file_path):
    y, sr = librosa.load(file_path, sr=None)
    fft_spectrum = np.abs(np.fft.fft(y))
    freqs = np.fft.fftfreq(len(fft_spectrum), 1 / sr)
    return freqs[np.argmax(fft_spectrum[:len(fft_spectrum)//2])]

def load_data(folder_path, has_labels=True):
    features, labels, file_names = [], [], []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".wav"):
            peak_freq = extract_peak_frequency(os.path.join(folder_path, file_name))
            features.append(peak_freq)
            if has_labels:
                labels.append(file_name.split("(")[0].strip())
            else:
                file_names.append(file_name)
    return np.array(features).reshape(-1, 1), (np.array(labels) if has_labels else file_names)

train_folder = "D:/داده‌های آموزش"
test_folder = "D:/داده‌های تست"

train_features, train_labels = load_data(train_folder)
test_features, test_file_names = load_data(test_folder, has_labels=False)

scaler = StandardScaler()
train_features = scaler.fit_transform(train_features)
test_features = scaler.transform(test_features)

label_encoder = LabelEncoder()
train_labels_encoded = label_encoder.fit_transform(train_labels)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(train_features, train_labels_encoded)

predicted_labels_encoded = knn.predict(test_features)
predicted_labels = label_encoder.inverse_transform(predicted_labels_encoded)

for file_name, predicted_label in zip(test_file_names, predicted_labels):
    print(f"File: {file_name} -> Predicted Label: {predicted_label}")

plt.figure(figsize=(12, 6))

# Training Data Plot
plt.subplot(1, 2, 1)
for label in np.unique(train_labels):
    idx = train_labels == label
    plt.scatter(train_features[idx], np.array([extract_peak_frequency(os.path.join(train_folder, fn)) for fn in os.listdir(train_folder) if fn.endswith(".wav")])[idx], label=label)
plt.title("Training Data")
plt.xlabel("Normalized Peak Frequency")
plt.ylabel("Peak Frequency (Hz)")
plt.xticks(rotation=45)
plt.legend()

# Test Data Plot
plt.subplot(1, 2, 2)
for label in np.unique(predicted_labels):
    idx = predicted_labels == label
    plt.scatter(test_features[idx], np.array([extract_peak_frequency(os.path.join(test_folder, fn)) for fn in test_file_names])[idx], label=label)
plt.title("Test Data")
plt.xlabel("Normalized Peak Frequency")
plt.ylabel("Peak Frequency (Hz)")
plt.xticks(rotation=45)
plt.legend()

plt.tight_layout()
plt.show()
