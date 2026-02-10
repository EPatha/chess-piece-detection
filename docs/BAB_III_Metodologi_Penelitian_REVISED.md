# BAB III  
# METODOLOGI PENELITIAN

## 3.1 Metode Pengumpulan Data

Penelitian ini menggunakan pendekatan **Research and Development (R&D)** dengan fokus pada pengembangan sistem deteksi catur berbasis Computer Vision dan Deep Learning. Metode R&D dipilih karena penelitian ini tidak hanya menghasilkan produk perangkat lunak, tetapi juga melakukan riset untuk meningkatkan akurasi deteksi melalui pendekatan hibrida yang menggabungkan teknik konvensional dan AI.

Pengumpulan data dalam penelitian R&D ini dilakukan melalui dua jalur utama: **data teoretis** untuk membangun landasan ilmiah dan **data empiris** untuk pelatihan serta pengujian model.

### 3.1.1 Pengumpulan Data Teoretis (Literature Review)

Pengumpulan informasi teoretis dilakukan dengan mengkaji jurnal ilmiah, buku, dan dokumentasi teknis terkait algoritma Computer Vision (OpenCV), arsitektur Deep Learning (YOLOv8), serta aturan standar catur (FIDE) untuk membangun landasan logika sistem.

**Sumber yang Dikaji:**
- **Jurnal Ilmiah**: Penelitian terkait algoritma Computer Vision untuk deteksi objek real-time dan arsitektur YOLO untuk object detection
- **Dokumentasi Teknis**: Dokumentasi resmi Ultralytics YOLOv8, spesifikasi standar FIDE, dan best practices PyQt5
- **Buku Referensi**: Literatur pengolahan citra digital dan integrasi GUI dengan sistem berbasis kamera

**Tujuan:** Memahami state-of-the-art teknologi deteksi objek, mengidentifikasi gap penelitian sebelumnya, dan merancang metode hibrida yang lebih robust.

---

### 3.1.2 Pengumpulan Dataset Citra (Image Dataset Acquisition)

Untuk melatih dan menguji model deteksi objek, penelitian ini menggunakan **data primer** guna memastikan model memiliki akurasi tinggi pada lingkungan implementasi.

#### A. Data Primer (Dataset Publik)

Data primer diperoleh dari repositori dataset terbuka seperti **Kaggle** dan **Roboflow**. Dataset ini mencakup ribuan citra bidak catur dengan berbagai jenis papan, gaya bidak, sudut pengambilan gambar, dan kondisi pencahayaan yang beragam. Hal ini penting agar model dapat mengenali fitur umum dari bidak catur (Raja, Ratu, dll.) secara universal.

**Karakteristik Dataset yang Dibutuhkan:**
1. **Variasi Papan Catur**: Berbagai material (kayu, vinyl, digital)
2. **Variasi Gaya Bidak**: Staunton style, modern design
3. **Variasi Sudut**: Top-down view hingga slight angle
4. **Variasi Pencahayaan**: Indoor, outdoor, backlight
5. **Variasi Background**: Solid hingga cluttered environment

Dataset akan dibagi menjadi **training set**, **validation set**, dan **test set** sesuai praktik standar machine learning.

#### B. Data Sekunder (Custom Capture)

Untuk validasi sistem pada lingkungan implementasi aktual, dilakukan pengambilan data tambahan menggunakan:
- **Perangkat**: Webcam USB dan Smartphone Android via DroidCam
- **Setup**: Papan catur standar turnamen dengan pencahayaan indoor
- **Tujuan**: Menguji robustness sistem pada kondisi real-world

---

### 3.1.3 Pra-pemrosesan dan Anotasi Data

Seluruh data yang terkumpul, baik dari sumber publik maupun hasil capture mandiri, melalui tahap preprocessing sebelum digunakan untuk training:

**A. Validasi Format Data**
- Verifikasi format anotasi YOLO (format: `class_id x_center y_center width height`)
- Pemeriksaan korespondensi antara gambar dan file anotasi

**B. Augmentasi Data**

Teknik augmentasi diterapkan untuk meningkatkan jumlah data training:
1. **Flip Horizontal**: Mencerminkan gambar
2. **Rotasi**: Rotasi ringan (±5°)
3. **Brightness Adjustment**: Variasi kecerahan (±20%)
4. **Saturation Adjustment**: Variasi saturasi warna (±15%)
5. **Gaussian Noise**: Penambahan noise ringan

**Tools yang Digunakan:**
- Roboflow built-in augmentation pipeline
- Albumentations library (Python)

---

## 3.2 Analisis Data

Setelah data terkumpul, tahap analisis dilakukan untuk memproses dan mengekstrak informasi yang relevan. Analisis data dalam penelitian R&D ini meliputi analisis kualitatif (design analysis) dan kuantitatif (performance metrics).

### 3.2.1 Perangkat Keras dan Perangkat Lunak

Perangkat yang digunakan untuk memproses dan menganalisis data adalah sebagai berikut:

#### A. Perangkat Keras

**Spesifikasi Komputer:**
- **Prosesor**: Apple M1 / Intel/AMD equivalent
- **RAM**: 8 GB atau lebih
- **Storage**: SSD untuk proses training yang cepat
- **Kamera**: Webcam USB 720p atau Smartphone Android (DroidCam)

#### B. Perangkat Lunak & Pustaka

**Bahasa Pemrograman dan Framework:**
- **Python 3.x**: Bahasa pemrograman utama
- **Ultralytics YOLO**: Framework untuk training, inference, dan evaluasi model
- **OpenCV**: Library untuk pemrosesan citra
- **PyQt5**: Framework GUI untuk antarmuka desktop aplikasi
- **python-chess**: Library untuk validasi logika permainan

**Pustaka Analisis dan Visualisasi:**
- **Matplotlib & Seaborn**: Visualisasi grafik dan Confusion Matrix
- **NumPy**: Operasi array untuk manipulasi matriks
- **Pandas**: Analisis statistik hasil pengujian

**Tools Pendukung:**
- **Visual Studio Code**: IDE untuk development
- **Git**: Version control system
- **Jupyter Notebook**: Untuk eksperimen dan analisis data

---

### 3.2.2 Cara Analisis (Analysis Methods)

Prosedur analisis data dilakukan melalui tiga tahapan evaluasi utama:

#### A. Analisis Kinerja Model Deteksi (YOLOv8)

Evaluasi ini bertujuan mengukur seberapa akurat model mengenali 12 kelas bidak catur. Metrik yang akan dianalisis meliputi:

**1. Confusion Matrix**  
Digunakan untuk memetakan kesalahan klasifikasi antar kelas (misalnya, seberapa sering sistem salah mengenali "Pion Putih" sebagai "Gajah Putih"). Analisis confusion matrix membantu mengidentifikasi pasangan kelas yang perlu ditingkatkan.

**2. Precision & Recall**  
Menghitung rasio ketepatan deteksi positif dan kemampuan model menemukan seluruh objek yang ada.
- **Precision**: Rasio deteksi benar terhadap total deteksi positif
- **Recall**: Kemampuan menemukan seluruh objek yang ada

**3. mAP (mean Average Precision)**  
Menggunakan standar mAP@0.5 dan mAP@0.5-0.95 untuk mendapatkan nilai tunggal yang merepresentasikan akurasi rata-rata model pada berbagai ambang batas (threshold).

**4. F1-Score**  
Menganalisis trade-off antara Precision dan Recall untuk menentukan threshold optimal.

---

#### B. Analisis Responsivitas Sistem (Real-Time Performance)

Analisis ini mengukur efisiensi sistem saat dijalankan secara langsung dalam kondisi operasional. Parameter yang akan diukur adalah:

**1. FPS (Frames Per Second)**  
Menghitung rata-rata jumlah bingkai yang dapat diproses sistem dalam satu detik untuk memastikan visualisasi berjalan mulus. Target minimum yang diharapkan adalah ≥25 FPS.

**2. Latensi (Latency)**  
Mengukur waktu tunda (dalam milidetik) mulai dari pergerakan bidak fisik hingga perubahan terdeteksi pada antarmuka digital. Komponen yang diukur meliputi:
- Camera capture latency
- Image preprocessing time
- YOLO inference time
- Chess validation time
- GUI update time

**3. Penggunaan Sumber Daya**
- **CPU Usage**: Persentase penggunaan CPU
- **Memory Usage**: RAM yang digunakan
- **GPU Utilization**: Jika tersedia

**Skenario Pengujian:** Sistem akan dijalankan selama durasi permainan penuh (10-15 menit) dengan monitoring berkelanjutan.

---

#### C. Analisis Akurasi Logika Permainan

Analisis fungsional dilakukan dengan membandingkan notasi PGN yang dihasilkan sistem secara otomatis dengan notasi manual (sebagai ground truth) dari serangkaian permainan uji coba. Analisis ini bertujuan memverifikasi keberhasilan algoritma Material Gain Heuristic dalam menangani situasi ambigu dan aturan langkah khusus.

**Metrik yang Digunakan:**
- **Move Accuracy**: Persentase langkah yang tercatat identik dengan ground truth
- **Special Move Handling**: Keberhasilan mendeteksi Castling, En Passant, Promotion
- **Ambiguity Resolution**: Akurasi dalam situasi ambigu

**Prosedur:**
1. Setup ground truth dengan pencatatan manual
2. Automatic capture menggunakan sistem
3. Comparison dan validation
4. Error analysis dan kategorisasi kesalahan

---

## 3.3 Metode yang Diusulkan

Untuk menyelesaikan permasalahan pelacakan posisi catur secara real-time dengan **akurasi tinggi** namun tetap **efisien secara komputasi**, penelitian ini mengusulkan **metode hibrida (Hybrid Logic-First Approach)** yang mengintegrasikan teknik Computer Vision konvensional dan Deep Learning.

Pendekatan hibrida ini dirancang dengan prinsip **"Visual Detection + Chess Logic Validation"**, di mana hasil deteksi visual tidak langsung diterima, tetapi melalui validasi menggunakan aturan logika catur untuk memastikan setiap langkah yang tercatat adalah legal dan valid.

### 3.3.1 Alur Kerja Sistem (System Workflow)

Alur kerja sistem dirancang dalam **lima tahapan sekuensial** sebagai berikut:

---

#### **Tahap 1: Akuisisi dan Pra-pemrosesan Citra**

Langkah awal dimulai dengan pengambilan citra dari kamera. Citra mentah (raw frame) diproses untuk memastikan kualitas input yang optimal bagi modul deteksi.

**Komponen Utama:**
- **Input**: Aliran video (video stream) dari kamera smartphone/webcam
- **Kalibrasi Papan**: Sistem mendeteksi empat titik sudut papan catur (secara manual atau otomatis) dan menerapkan Transformasi Perspektif (Perspective Transform) untuk mengubah citra miring menjadi pandangan atas (top-down view) berukuran 600×600 piksel
- **Filtering**: Penerapan Gaussian Blur pada citra hasil transformasi untuk mengurangi noise visual akibat variasi pencahayaan

**Algoritma yang Digunakan:**
- Canny Edge Detection untuk deteksi sudut papan
- Perspective Transform (cv2.getPerspectiveTransform)
- Morphological operations untuk noise reduction

---

#### **Tahap 2: Deteksi Okupansi Berbasis Analisis Warna**

Tahap ini berfungsi sebagai **filter awal yang ringan** untuk mendeteksi adanya perubahan sebelum menjalankan klasifikasi YOLO yang lebih berat.

**Algoritma:**
- Konversi ROI ke HSV color space
- Analisis nilai Hue, Saturation, Value untuk klasifikasi
- Logika threshold untuk menentukan status: empty, white, black, atau colored

**Logika:**  
Menghitung nilai HSV rata-rata pada setiap kotak (grid 8×8). Jika nilai Value rendah → kotak kosong; jika Saturation rendah + Value tinggi → bidak putih; jika Saturation rendah + Value rendah → bidak hitam.

**Output:** Matriks 8×8 yang merepresentasikan status okupansi papan.

**Keunggulan:** Sangat cepat (~25ms) dan berfungsi sebagai trigger untuk aktivasi YOLO.

---

#### **Tahap 3: Klasifikasi Objek dengan Deep Learning (YOLOv8)**

Jika tahap deteksi okupansi mengindikasikan adanya perubahan posisi yang stabil (setelah debounce time), modul AI diaktifkan untuk identifikasi detail.

**Model:** Menggunakan arsitektur YOLOv8n (Nano) yang telah dilatih ulang (fine-tuned) dengan dataset bidak catur.

**Proses:**
1. Model memindai area papan (Region of Interest)
2. Mengklasifikasikan objek ke dalam 12 kelas (6 jenis bidak × 2 warna)
3. Memberikan koordinat bounding box dan confidence score

**Hyperparameters Training:**
- Epochs: 50
- Batch size: 16
- Learning rate: 0.01 (initial)
- Optimizer: SGD with momentum
- Data augmentation: Flip, rotation, brightness adjustment

**Output:** Daftar deteksi berisi Label Kelas, Koordinat Bounding Box, dan Skor Keyakinan (Confidence Score).

---

#### **Tahap 4: Inferensi Logika Permainan (Game Logic Inference)**

Data visual diterjemahkan menjadi notasi catur yang valid.

**Komponen Utama:**

**A. Pemetaan Visual ke Board State**  
Menggabungkan hasil deteksi visual dengan status papan internal (internal board state) dari pustaka python-chess.

**B. Deteksi Perubahan**  
Membandingkan grid saat ini dengan grid stabil sebelumnya untuk mengidentifikasi kotak yang berubah.

**C. Inferensi Move dari Pattern**  
Berdasarkan jumlah kotak yang berubah:
- 0 changes: Tidak ada move
- 1 change: Promotion/Piece removed
- 2 changes: Normal move/Capture
- 3 changes: En Passant
- 4 changes: Castling
- >4 changes: Error/Multiple moves

**D. Validasi Langkah**  
Memeriksa apakah perpindahan dari posisi A ke posisi B merupakan langkah legal menurut aturan FIDE menggunakan library python-chess.

**E. Penyelesaian Ambiguitas**  
Jika terdapat lebih dari satu kemungkinan langkah legal yang sesuai dengan perubahan visual (misal: dua Kuda bisa memakan ke kotak yang sama), sistem menerapkan **algoritma Material Gain Heuristic** untuk memilih langkah dengan probabilitas keuntungan material tertinggi.

**Material Values:**
- Pawn: 1
- Knight/Bishop: 3
- Rook: 5
- Queen: 9

---

#### **Tahap 5: Pembangkitan Output (Output Generation)**

Setelah langkah terverifikasi valid:

**A. Update State**  
Memperbarui status papan internal menggunakan python-chess.

**B. Pencatatan**  
Menambahkan langkah ke dalam daftar notasi PGN (Portable Game Notation).

**C. Umpan Balik Visual**
- Update tampilan papan digital 2D
- Highlight last move (source dan destination)
- Highlight best move dari engine (jika aktif)
- Update material count

**D. Umpan Balik Audio**  
Memperbarui tampilan GUI dan memicu modul Text-to-Speech untuk menyuarakan langkah tersebut (misal: "Knight to f3").

---

### 3.3.2 Keunggulan Metode Hibrida yang Diusulkan

Pendekatan **Hybrid Logic-First** memberikan beberapa keunggulan dibanding metode tunggal:

**1. Koreksi Otomatis**  
Jika YOLO salah klasifikasi jenis piece, chess logic mengoreksi berdasarkan legal moves dan game state history.

**2. Redundancy**  
Jika YOLO gagal detect (confidence rendah), sistem fallback ke color detection + logic inference.

**3. Validation**  
Semua move divalidasi dengan chess.Board.is_legal() sebelum diaplikasikan → mencegah illegal moves.

**4. Stability Check**  
Requirement 5 frame konsisten mengurangi false positive (deteksi noise atau transient objects).

**5. Ambiguity Resolution**  
Algoritma Material Gain Heuristic memberikan solusi deterministik untuk situasi ambigu.

---

## 3.4 Metode Pengembangan Sistem

Selain pengembangan model cerdas, penelitian ini juga mencakup pembangunan perangkat lunak aplikasi desktop (Desktop Application) sebagai antarmuka pengguna. Metode pengembangan sistem yang digunakan adalah **model Prototyping**. 

Model ini dipilih karena karakteristik aplikasi berbasis visi komputer memerlukan **iterasi berulang** untuk menyelaraskan responsivitas antarmuka dengan kecepatan pemrosesan video real-time.

### 3.4.1 Alasan Pemilihan Model Prototyping

**Karakteristik yang Sesuai:**
1. **Ketidakpastian Requirement**: Parameter deteksi (threshold, confidence) tidak dapat ditentukan pasti di awal
2. **User Feedback Centric**: Desain GUI perlu disesuaikan berdasarkan feedback
3. **Rapid Iteration**: Perlu iterasi cepat untuk testing berbagai konfigurasi
4. **Incremental Feature Addition**: Fitur dapat ditambahkan bertahap

**Keuntungan:**
- User dapat mencoba prototype sejak tahap awal
- Feedback dapat segera diintegrasikan
- Mengurangi risiko kesalahan requirement
- Memungkinkan parallel development

---

### 3.4.2 Tahapan Pengembangan Sistem

#### **Tahap 1: Analisis Kebutuhan (Requirement Analysis)**

Tahap ini mendefinisikan spesifikasi teknis perangkat lunak yang dibutuhkan untuk menjalankan sistem secara optimal.

**A. Kebutuhan Fungsional**

Aplikasi harus mampu:
1. **Camera Management**: Deteksi dan koneksi ke kamera (Webcam/DroidCam), menampilkan stream video real-time
2. **Board Calibration**: Auto-detect papan catur, manual calibration, perspective transform
3. **Piece Detection**: Toggle antara Color dan YOLO Detection, adjustable parameters via GUI
4. **Game Logic**: Validasi langkah, detect special moves, move history tracking
5. **Visualization**: Visualisasi papan digital 2D, highlight moves, material count
6. **Data Export**: Export PGN, save FEN notation
7. **Audio Feedback**: Text-to-speech announcement untuk setiap move
8. **Engine Integration**: Interface ke Stockfish untuk analisis dan best move suggestion

**B. Kebutuhan Non-Fungsional**

1. **Performance**: Frame rate ≥25 FPS, latency <100ms, memory <500 MB
2. **Usability**: Antarmuka intuitif, responsive UI
3. **Reliability**: Tidak crash selama permainan penuh, graceful error handling
4. **Maintainability**: Modular code (MVC pattern), comprehensive logging

**C. Kebutuhan Antarmuka**

Diperlukan antarmuka grafis (GUI) yang responsif, memiliki tombol kontrol (Mulai, Stop, Kalibrasi, Putar Papan), dan panel pengaturan parameter deteksi (Threshold/Confidence) yang dapat diubah secara live.

---

#### **Tahap 2: Perancangan Sistem dan Antarmuka (System & UI Design)**

Pada tahap ini, dilakukan perancangan arsitektur perangkat lunak dan tata letak visual aplikasi.

**A. Pemilihan Framework GUI**

**Framework Terpilih:** PyQt5

**Alasan Pemilihan:**
1. **Multithreading Support**: QThread untuk memisahkan proses berat dari UI thread
2. **Signal-Slot Mechanism**: Event-driven architecture untuk real-time system
3. **Rich Widget Library**: Built-in widgets untuk video display, sliders, buttons
4. **Cross-Platform**: Berjalan di macOS, Windows, Linux
5. **Mature & Well-Documented**: Komunitas besar dan dokumentasi lengkap

**B. Desain Arsitektur Perangkat Lunak**

Mengadopsi **Model-View-Controller (MVC) Pattern**:
- **View (UI Layer)**: MainWindow, Camera Panels, Board View
- **Controller (Logic Layer)**: HybridManager, ProcessingThread, CameraThread
- **Model (Data Layer)**: StateManager, Board (python-chess), ConfigManager

**C. Desain Tata Letak**

Antarmuka dirancang dengan pembagian tiga panel utama:
1. **Panel Video**: Menampilkan input kamera asli dengan overlay deteksi
2. **Panel Digital**: Menampilkan representasi papan catur 2D yang bersih (gaya Lichess)
3. **Panel Kontrol & Log**: Berisi tombol operasi, slider pengaturan, dan daftar notasi langkah

**D. Alur Data**

Merancang mekanisme **Signal and Slot** (fitur PyQt) untuk mengirimkan data koordinat bidak dari modul pemrosesan citra ke modul tampilan visual secara real-time.

**Keuntungan Signal-Slot:**
- Decoupling: Komponen tidak perlu referensi langsung
- Thread-safe: Qt otomatis handle signal antar thread
- Event-driven: Responsif terhadap perubahan state

---

#### **Tahap 3: Implementasi dan Pengkodean (Implementation)**

Tahap ini merupakan realisasi rancangan ke dalam kode program menggunakan bahasa Python.

**A. Setup Proyek**

Struktur direktori modular:
```
chess-mind-hybrid/
├── chess_hybrid/
│   ├── chess_mind_app.py          # Entry point
│   ├── config.json                # Configuration
│   ├── core/                      # Core logic
│   ├── ui/                        # User Interface
│   └── utils/                     # Utilities
├── models/                        # Trained models
└── requirements.txt               # Dependencies
```

**B. Integrasi OpenCV dan PyQt**

Mengimplementasikan konversi format citra dari OpenCV (BGR) ke format Qt (QImage/QPixmap) agar video dapat ditampilkan pada widget label GUI.

**C. Manajemen Thread**

Membuat Worker Thread terpisah untuk menjalankan algoritma YOLOv8 dan deteksi tepi, sehingga proses inferensi yang berat tidak mengganggu responsivitas tombol-tombol pada antarmuka utama.

**Implementasi:**
- **CameraThread**: Capture video dalam thread terpisah
- **ProcessingThread**: YOLO inference dalam thread terpisah
- **Signal-Slot**: Komunikasi thread-safe antar komponen

**D. Implementasi Fitur Pendukung**

Menambahkan pustaka pyttsx3 untuk fitur Text-to-Speech dan python-chess untuk validasi logika di balik layar.

---

#### **Tahap 4: Pengujian Prototipe (Prototyping Testing)**

Prototipe aplikasi yang telah dibangun diuji menggunakan metode **Black Box Testing**.

**A. Fokus Pengujian**

Memastikan seluruh tombol fungsi (Kalibrasi, Start Game, Undo Move, Export PGN) berjalan sesuai fungsinya tanpa melihat kode internal.

**B. Uji Responsivitas**

Menguji apakah slider pengaturan parameter dapat mempengaruhi hasil deteksi secara langsung (real-time) tanpa perlu me-restart aplikasi.

**C. Evaluasi**

Jika ditemukan lag atau crash saat pemrosesan video jangka panjang, dilakukan optimasi pada manajemen memori dan thread sebelum sistem dinyatakan final.

**Iterasi:** Berdasarkan feedback testing, dilakukan perbaikan dan refinement sebelum deployment.

---

#### **Tahap 5: Deployment dan Dokumentasi**

**A. Packaging Aplikasi**

Untuk distribusi ke user akhir, aplikasi di-bundle menggunakan PyInstaller menjadi executable yang dapat dijalankan tanpa install Python.

**B. Dokumentasi**

Membuat dokumentasi end-user (Installation Guide, Quick Start, Troubleshooting) dan dokumentasi developer (Code documentation, Architecture diagram, API reference).

---

## 3.5 Metode Pengujian

Untuk memvalidasi efektivitas metode hibrida yang diusulkan, dilakukan serangkaian pengujian sistematis yang mencakup tiga aspek utama: **akurasi deteksi**, **kinerja komputasi**, dan **keandalan fungsional**.

### 3.5.1 Pengujian Akurasi Model (Model Accuracy Testing)

Pengujian ini bertujuan mengukur kemampuan model YOLOv8 dalam mengklasifikasikan bidak catur secara tepat.

**A. Dataset Uji**

Menggunakan **test set** yang dipisahkan dari awal (tidak pernah dilihat model selama training). Umumnya 10-20% dari total dataset.

**B. Metrik Evaluasi**

**1. mAP (mean Average Precision)**  
Menghitung rata-rata presisi pada Intersection over Union (IoU) threshold 0.5 (mAP@50) untuk melihat ketepatan area deteksi. Metrik ini merepresentasikan akurasi rata-rata model pada berbagai ambang batas overlap.

**2. Confusion Matrix**  
Menganalisis matriks kesalahan untuk mengidentifikasi kelas bidak mana yang paling sering salah dikenali (misal: kemiripan visual antara Pion dan Gajah). Analisis diagonal matrix menunjukkan True Positives, sedangkan off-diagonal menunjukkan misclassifications.

**3. Precision & Recall**  
Mengukur rasio deteksi benar terhadap total deteksi positif dan total objek sebenarnya.
- **Precision = TP / (TP + FP)**
- **Recall = TP / (TP + FN)**
- **F1-Score = 2 × (Precision × Recall) / (Precision + Recall)**

**C. Prosedur Pengujian**

Menggunakan Ultralytics CLI untuk validation mode yang akan menghasilkan:
- Confusion matrix visualization
- Precision-Recall curve
- Metrics summary (JSON/CSV)

---

### 3.5.2 Pengujian Kinerja Sistem (System Performance Testing)

Pengujian ini dilakukan untuk memastikan sistem mampu berjalan secara **real-time** pada perangkat target (Laptop standar/PC tanpa GPU high-end).

**A. Skenario Pengujian**

Menjalankan sistem selama durasi permainan penuh (±10 menit) dengan input kamera smartphone via USB.

**B. Parameter Ukur**

**1. FPS (Frames Per Second)**  
Mencatat rata-rata frame rate selama operasi. Target minimal adalah **≥25 FPS** untuk kelancaran visual.

**Metrics:**
- Average FPS: Rata-rata selama sesi
- Min/Max FPS: Worst case dan best case
- Standard Deviation: Stabilitas frame rate

**2. Latensi Inferensi**  
Mengukur waktu rata-rata yang dibutuhkan sistem untuk memproses satu langkah (mulai dari bidak diletakkan hingga notasi muncul di layar).

**Breakdown Latensi:**
- Camera capture: ~16-33ms
- Preprocessing: ~5-10ms
- YOLO inference: ~40-60ms
- Chess validation: ~5-10ms
- GUI update: ~10ms

**Target Total:** < **100ms** untuk user experience yang responsif.

**3. Penggunaan Sumber Daya**  
Memantau persentase penggunaan CPU dan RAM selama aplikasi berjalan.
- **CPU Usage**: Target < 70%
- **Memory Usage**: Target < 500 MB
- **GPU Utilization**: Jika tersedia

**C. Logging dan Reporting**

Semua metrics dicatat ke log file (CSV) untuk analisis post-testing.

---

### 3.5.3 Pengujian Fungsional & Skenario Permainan (Functional Testing)

Pengujian ini memvalidasi logika sistem dalam menangani situasi permainan nyata.

**A. Prosedur Pengujian**

Memainkan **5 partai catur utuh** dengan berbagai skenario langkah untuk menguji robustness sistem.

**Setup:**
- Papan: Standard tournament board (50cm × 50cm)
- Pieces: Staunton style
- Pencahayaan: Indoor ~400 lux
- Operator: 2 pemain manusia

**B. Skenario Uji**

**1. Langkah Normal (Normal Moves)**  
Pemindahan bidak standar tanpa special rules (Pawn, Knight, Bishop, Rook, Queen, King moves).

**2. Langkah Khusus (Special Moves)**

**A. Castling (Rokade)**
- Kingside Castling (0-0): 4 kotak berubah simultan
- Queenside Castling (0-0-0): 4 kotak berubah simultan
- **Challenge**: Sistem harus recognize pattern

**B. En Passant Capture**
- Setup: Pawn double push melewati capture square
- **Challenge**: 3 kotak berubah dengan pattern unusual

**C. Pawn Promotion**
- Setup: Pawn mencapai rank 8
- **Challenge**: Visual tidak bisa otomatis tahu user pilih Queen/Rook/Bishop/Knight
- **Expected**: Dialog pemilihan promotion piece

**3. Situasi Ambigu (Ambiguous Situations)**  
Melakukan langkah memakan (capture) di mana **dua bidak sejenis dapat menuju kotak yang sama**, untuk menguji algoritma Material Gain Heuristic.

**Example:** Dua Knights bisa sama-sama move ke kotak yang sama → sistem harus memilih berdasarkan material gain.

**C. Validasi (Ground Truth Comparison)**

Membandingkan file PGN yang dihasilkan sistem secara otomatis dengan notasi manual yang dicatat oleh manusia. Tingkat keberhasilan diukur berdasarkan persentase langkah yang tercatat valid dan sesuai aturan FIDE.

**Prosedur:**
1. **Manual Recording**: Operator mencatat notasi manual (ground truth)
2. **Automatic Recording**: Sistem generate PGN otomatis
3. **Comparison**: Move-by-move comparison menggunakan python-chess
4. **Error Analysis**: Kategorisasi kesalahan (False Move, Missed Move, Misclassification)

**D. Metrics**

**Move Accuracy** = (Jumlah Move Benar / Total Move) × 100%

**Target Minimum:** ≥ **95%** move accuracy pada kondisi normal.

---

## Ringkasan Metodologi

Penelitian ini menggunakan metode **Research and Development (R&D)** dengan tahapan lengkap:

1. **Pengumpulan Data**: Literature review + Dataset publik (citra bidak catur dengan variasi) + Custom capture
2. **Analisis Data**: Evaluasi model (mAP, Confusion Matrix, Precision/Recall) + Performance metrics (FPS, Latency, Resource usage) + Game logic validation
3. **Metode yang Diusulkan**: Hybrid Logic-First Approach (5 tahap: Akuisisi → Color Detection → YOLO → Chess Validation → Output)
4. **Pengembangan Sistem**: Prototyping model dengan PyQt5 (MVC pattern, Multithreading, Signal-Slot)
5. **Pengujian**: Akurasi model + Kinerja sistem + Fungsional (special moves, ambiguity resolution)

Metode hibrida yang diusulkan menggabungkan kecepatan Color Detection, akurasi YOLO, dan validitas Chess Logic untuk menghasilkan sistem yang robust dan efisien.
