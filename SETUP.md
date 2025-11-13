# Rosy Tax Processor - Quick Setup Guide

🚀 **Welcome to Rosy Tax Processor!** 

An AI-powered system for processing tax documents and generating completed Form 1040 PDFs.

## 📋 **Quick Start (For Your Friend)**

### **1. Prerequisites**
- **Python 3.12+** - Download from [python.org](https://python.org)
- **Git** (optional) - For cloning the repository

### **2. Installation**
```powershell
# Clone the repository
git clone https://github.com/sabs-27/Tax-Processor.git
cd Tax-Processor

# Install dependencies (this may take a few minutes on first run)
pip install -r requirements.txt
```

### **3. Run the Application**
```powershell
# Start the server
python backend.py
```

🌐 **Open your browser and visit:** `http://localhost:5000`

### **4. Usage**
1. **Upload** your W-2 or 1099 PDF files
2. **Review** the extracted fields (edit if needed)
3. **Download** your completed Form 1040 PDF

## 🛠 **Troubleshooting**

### **If you get "tesseract not installed" error:**
- **Solution 1 (Recommended):** Use PDF files instead of images
- **Solution 2:** Install Tesseract OCR from [here](https://github.com/UB-Mannheim/tesseract/releases)

### **If port 5000 is busy:**
```powershell
# Use a different port
python -c "from backend import app; app.run(port=5001)"
# Then visit: http://localhost:5001
```

### **If dependencies fail to install:**
```powershell
# Try upgrading pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 📱 **What You Can Process**
- ✅ **W-2 forms** (wages and withholding)
- ✅ **1099 forms** (miscellaneous income)
- ✅ **PDF files** (preferred - no OCR needed)
- ✅ **Text files** (for testing)
- ✅ **Image files** (PNG, JPG - requires Tesseract)

## 🎯 **Example Workflow**
1. Upload your W-2 PDF → System extracts: wages=$50,000, withholding=$5,000
2. Review fields → Edit if any values look wrong
3. Select filing status (Single/Married) 
4. Click "Finalize & Download PDF" → Get completed Form 1040!

## 🧪 **Test the System**
Try uploading the sample file: `samples/sample_w2.txt`

## ⚡ **Performance Notes**
- **First run:** Takes 1-2 minutes (downloads AI models ~500MB)
- **Subsequent runs:** Very fast (<3 seconds per document)
- **Internet required:** Only for first-time model download

## 🔒 **Privacy & Security**
- ✅ All processing happens **locally** on your computer
- ✅ **No data sent to external servers**
- ✅ Files automatically cleaned up after processing
- ✅ SSNs masked in API responses for security

## 📞 **Need Help?**
- Check the main [README.md](README.md) for detailed documentation
- Run tests: `python -m pytest` to verify everything works
- Look at sample files in the `samples/` folder

## 🎉 **Enjoy Your Automated Tax Processing!**

**Built by sabs-27 • 100% Complete • Production Ready**

---
*Note: This is a demonstration system. For actual tax filing, always review the generated forms carefully and consult a tax professional if needed.*