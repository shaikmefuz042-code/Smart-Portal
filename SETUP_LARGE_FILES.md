# Setting Up Large Files

This project uses large machine learning model files that exceed GitHub's 100MB file limit. Follow these steps to set them up locally.

## Files to Download/Generate

### 1. Face Recognition Model (`model/face_model.h5`)
The trained Keras model file (~273 MB) is required for face recognition.

**Option A: Download Pre-trained Model**
- Contact the project maintainer for the model file
- Place it in: `model/face_model.h5`

**Option B: Train Your Own Model**
```bash
cd model
python train_model.py
```

This will generate `face_model.h5` from your training dataset.

---

### 2. dlib Library (`backend/dlib-19.24.6-cp310-cp310-win_amd64.whl`)
Pre-built dlib wheel for Python 3.10 on Windows.

**Installation:**
```bash
pip install backend/dlib-19.24.6-cp310-cp310-win_amd64.whl
```

Or install directly from PyPI:
```bash
pip install dlib
```

---

## Directory Structure After Setup

```
smart-portal/
├── backend/
│   ├── dlib-19.24.6-cp310-cp310-win_amd64.whl    (if keeping locally)
│   └── ...
├── model/
│   ├── face_model.h5                             (REQUIRED)
│   ├── train_model.py
│   └── ...
└── ...
```

---

## Complete Setup Instructions

1. **Clone Repository**
   ```bash
   git clone https://github.com/shaikmefuz042-code/smart-portal.git
   cd smart-portal
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Large Files**
   - Download `face_model.h5` or train it using `python model/train_model.py`
   - Place in `model/` directory

5. **Run Application**
   ```bash
   cd backend
   python app.py
   ```

6. **Access Application**
   - Open browser to `http://localhost:5000`

---

## Troubleshooting

**Error: `FileNotFoundError: model/face_model.h5`**
- Ensure the model file is in the `model/` directory
- Either download it or train a new one

**Error: `ImportError: No module named 'dlib'`**
- Install dlib: `pip install dlib`
- Or use the wheel: `pip install backend/dlib-19.24.6-cp310-cp310-win_amd64.whl`

---

## Contact

For pre-trained model files or additional setup help, contact the project maintainer.
