# BAB V - KESIMPULAN DAN SARAN

## 5.1 Kesimpulan

Penelitian ini berhasil mengembangkan **ChessMind Hybrid Vision System** dengan hasil:

1. **Deteksi Papan**: Tingkat keberhasilan 95% dalam pencahayaan normal
2. **Model YOLOv8**: Precision 98.4%, Recall 99.3%, mAP@50 98.8%
3. **Hybrid Approach**: Akurasi 96-98%, false positive <1%
4. **Real-time**: 28-30 FPS, latency 80-85ms pada Apple M1
5. **GUI**: Antarmuka PyQt5 dengan arsitektur MVC yang responsif

## 5.2 Perbandingan dengan Penelitian Sebelumnya

| Penelitian | Akurasi | FPS | Metode |
|-----------|---------|-----|--------|
| Naik & Taru (2025) | 97.2% | ~30 | YOLOv8 only |
| Dutta et al. (2024) | ~95% | 30 | YOLOv8 real-time |
| Bugarin (2024) | ~90% | 22 | CV + ML |
| Yadav et al. (2024) | 93% | 24 | Custom CV |
| **Penelitian Ini** | **96-98%** | **28-30** | **Hybrid + Logic** |

**Keunggulan penelitian ini:**
- Akurasi tertinggi dengan validasi chess logic
- Efisiensi pada mid-range hardware (Apple M1)
- Complete end-to-end system

## 5.3 Keterbatasan

- Kamera minimal 720p, pencahayaan 400-600 lux
- Occlusion ekstrem masih menjadi tantangan
- Promotion memerlukan input manual
- Dataset terbatas pada Staunton-style pieces

## 5.4 Saran

### Pengembangan Sistem
1. Adaptive lighting compensation
2. Automatic promotion detection
3. Model quantization untuk optimasi
4. Cloud sync dan online integration

### Penelitian Lanjutan
1. Transformer-based models (ViT, DETR)
2. 3D reconstruction dengan stereo vision
3. Edge deployment (Raspberry Pi, Jetson)
4. Robot arm integration

### Aplikasi Praktis
1. Educational tool dengan tutorial mode
2. Tournament support dengan live broadcast
3. Accessibility (voice control, braille)
4. Streaming integration (OBS, Twitch)

## 5.5 Penutup

Sistem ini mencapai akurasi 96-98% dengan pendekatan Hybrid Logic-First, unggul dibanding penelitian sebelumnya. Implementasi modern (YOLOv8, PyQt5, Stockfish) dengan arsitektur well-designed menghasilkan sistem yang maintainable dan scalable untuk pengembangan masa depan.