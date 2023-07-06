# projectEncrypt
This project provides a safe way to create a verified virtual identity without storing any user information. 

The project uses [OpenCV](https://link-url-here.org](https://pypi.org/project/opencv-python/)https://pypi.org/project/opencv-python/) for computer vision to detect
the [MRZ](https://en.wikipedia.org/wiki/Machine-readable_passport) (Machine Readable Zone) on an ID document. Once detected, text is extracted from the 
MRZ using a [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) model, which is trained on a [dataset](https://github.com/DoubangoTelecom/tesseractMRZ/tree/master/tessdata_best) 
of 7000 samples.
