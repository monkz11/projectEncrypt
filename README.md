# projectEncrypt 🛂
projectEncrypt is an open source identity verification app that allows users to prove their identitiy using a government issued ID. IDs are used for verification, but none of the information is stored. The only information stored for a user is their username, password, and email/phone number. The project was created to combat bot accounts by providing a safe way to prove human identitiy.

The project uses [OpenCV](https://pypi.org/project/opencv-python/) for computer vision to detect the [MRZ](https://en.wikipedia.org/wiki/Machine-readable_passport) (Machine Readable Zone) on an ID document. 

Images undergo various stages of pre-processing to detect the location of the MRZ:

<img width="448" alt="image" src="https://github.com/monkz11/projectEncrypt/assets/82888595/e0b2af1c-d5f2-48e4-aab2-162f897fdc9d">
<img width="448" alt="image" src="https://github.com/monkz11/projectEncrypt/assets/82888595/1e90c638-2bdf-453c-9ec3-78694b8bc7d3">
<img width="448" alt="image" src="https://github.com/monkz11/projectEncrypt/assets/82888595/5171e09d-a5aa-4370-b09d-8cc3b7533f0a">
<img width="448" alt="image" src="https://github.com/monkz11/projectEncrypt/assets/82888595/3bc808ae-80ee-4c9a-9d12-c876d4e3d477">

Once detected, text is extracted from the MRZ using a [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) model, which is trained on a [dataset](https://github.com/DoubangoTelecom/tesseractMRZ/tree/master/tessdata_best) of 7000 samples.

<img width="100%" alt="image" src="https://github.com/monkz11/projectEncrypt/assets/82888595/d3296bc4-b253-4422-9e2d-55cfdec111e7">




