# Rebuid Circuit From Bread Board

This project is focused on extracting the abstract circuit connection relationship from a picture of a breadboard and recreating the circuit diagram. It is designed to assist students majoring in electric in the process of learning and experimenting with breadboards.

Often, when circuits become too large and complex, it can be difficult to determine the exact connections between different elements on the breadboard. This project aims to alleviate this issue by extracting the connection information from a picture of the breadboard and creating an accurate circuit diagram.

By providing a more visual and organized representation of the circuit, students can better understand the connections between different components and how they contribute to the overall circuit. This can help students to more effectively learn and experiment with breadboards, ultimately improving their understanding of electrical circuits.

## Run the project

Run the following in the command line :

```txt
git clone https://github.com/JoeLeelyf/breadboard-component-classification.git
cd breadboard-component-classification
conda creat -n breadboard-classification
conda activate breadboard-classification
pip install -r requirements.txt
```

Then open the "breadoard-elements-detect.ipynb" file, all results are showed in the jupter notebook.



## Structure of the project

```txt
.
├── README.md
├── breadoard-elements-detect.ipynb # main file
├── images 													# images sets
│   ├── result
│   │   └── test_1_result.jpg
│   ├── temp
│   │   └── test_1_breadboard.jpg
│   └── test
│       └── test_1.jpeg
├── models
│   ├── __init__.py
│   ├── common.py
│   ├── experimental.py
│   └── yolo.py
├── requirements.txt
├── runs
│   └── detect
│       └── exp
├── tools
│   ├── circuit_draw.py
│   └── detection.py
├── utils
│   ├── __init__.py
│   ├── activations.py
│   ├── add_nms.py
│   ├── autoanchor.py
│   ├── aws
│   │   ├── __init__.py
│   │   ├── mime.sh
│   │   ├── resume.py
│   │   └── userdata.sh
│   ├── datasets.py
│   ├── general.py
│   ├── google_app_engine
│   │   ├── Dockerfile
│   │   ├── additional_requirements.txt
│   │   └── app.yaml
│   ├── google_utils.py
│   ├── loss.py
│   ├── metrics.py
│   ├── plots.py
│   ├── torch_utils.py
│   └── wandb_logging
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-311.pyc
│       │   └── wandb_utils.cpython-311.pyc
│       ├── log_dataset.py
│       └── wandb_utils.py
└── weights 													# pretained weights
    └── breadboard.pt
```



## Details Info

### Part I: Elements Segment

This part was accomplished using YoloV7. Using yolov7.pt as the pretrained weights, after 600 epcho, this model's outcome is as below:

<img src="https://other-file-access-by-internet.oss-cn-beijing.aliyuncs.com/%E4%B8%8B%E8%BD%BD.png?Expires=1686145078&OSSAccessKeyId=TMP.3Kh8NuFbJtfZeGMMM4noJ1grHcc1EqP71VYy2mrD6rAMP6o9wXptiitJxCs7GHod8mqEMLLckNoveKYictMDc67bVws8PR&Signature=CVMB%2FwCMrhJLmT8maSiR6253xlo%3D" alt="下载" style="zoom:36%;" />

Result on our test sets:

<img src="https://other-file-access-by-internet.oss-cn-beijing.aliyuncs.com/%E6%88%AA%E5%B1%8F2023-06-07%2020.30.12.png?Expires=1686145063&OSSAccessKeyId=TMP.3Kh8NuFbJtfZeGMMM4noJ1grHcc1EqP71VYy2mrD6rAMP6o9wXptiitJxCs7GHod8mqEMLLckNoveKYictMDc67bVws8PR&Signature=YyQV2WQIRhM7Csb%2BcTYTwILuzIk%3D" alt="截屏2023-06-07 20.30.12" style="zoom:50%;" />

Datasets were uploaded to Kaggle: [BreadBoard Eletronic Component Datasets | Kaggle](https://www.kaggle.com/datasets/lyfjoelee/breadboard-eletronic-component-datasets)



### Part II: Get Abstract Circuit Connection Relationship

The fixed connections on a breadboard determine that certain holes are on the same voltage level. This means that the connections between elements in a circuit can be completely determined by the number of voltage levels and the location of each component's ends on these levels.

To begin mapping out the circuit, we use cv2.findContours() with specific filters to identify all the holes on the breadboard. From there, we can determine which holes are on the same voltage level. The results are shown below, where holes on the same voltage level are enclosed by red rectangles.

<img src="https://other-file-access-by-internet.oss-cn-beijing.aliyuncs.com/output.png?Expires=1686144987&OSSAccessKeyId=TMP.3Kh8NuFbJtfZeGMMM4noJ1grHcc1EqP71VYy2mrD6rAMP6o9wXptiitJxCs7GHod8mqEMLLckNoveKYictMDc67bVws8PR&Signature=Utk1rNu6Wa7oregnw68Pf6uSPhY%3D" style="zoom:50%;" />

Each column or row enclosed by a red rectangle represents a different voltage level, unless they are connected by a wire. By determining the position of the bounding box (provided by Yolo) corresponding to the column or row, we can abstract the connection relationship of the circuits.

The results are presented in the following format:

```txt
 [('Resistor', 0, 1), ('Resistor', 0, 2), ('Resistor', 0, 3), ('Resistor', 1, 3), ('Resistor', 2, 4), ('Resistor', 1, 4)]
```



### Part III: Draw Circuit From The Abstract Connection Relationship

This part uses python model SchewDraw. 

<img src="https://other-file-access-by-internet.oss-cn-beijing.aliyuncs.com/output1.png?Expires=1686145015&OSSAccessKeyId=TMP.3Kh8NuFbJtfZeGMMM4noJ1grHcc1EqP71VYy2mrD6rAMP6o9wXptiitJxCs7GHod8mqEMLLckNoveKYictMDc67bVws8PR&Signature=Ao9VdY%2FBCgXDuyrNvXkm952ckcU%3D" style="zoom:70%;" />