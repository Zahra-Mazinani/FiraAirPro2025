# FiraAirPro2025
SkyXel Robotic Team
A project by the SkyXel Robotic Team aiming to develop advanced robotic solutions for the FiraAirPro2025 competition.
## Table of Contents
- [About the Project](#about-the-project)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Fake Tello](#fake-tello)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)


## About the Project
The FiraAirPro2025 project is developed by the SkyXel Robotic Team. This project focuses on building innovative robotic solutions to compete in the FiraAirPro2025 competition.


The main task of the FiraAirPro2025 competition is divided into two key parts.
The first part involves gate detection and alignment of the drone to successfully pass through rectangular gates. This requires accurate visual processing and precise control to ensure the drone navigates through each gate efficiently.


The second part focuses on line detection and following. In this phase, the drone must detect a track line on the ground and autonomously follow it using real-time visual feedback and motion control algorithms.

These challenges were addressed using multithreaded processing and classical computer vision techniques. By separating image processing and control tasks into parallel threads, the system ensures real-time performance and responsiveness.

Additionally, the drone is controlled using a PID (Proportional-Integral-Derivative) controller, which provides smooth and stable flight behavior while navigating through gates and following lines.



## Getting Started
To get a local copy up and running follow these simple steps.

### Installation
1. Clone the repo
   ```sh
   git clone https://github.com/Zahra-Mazinani/FiraAirPro2025.git

   pip install -r requirements.txt

## Usage
1. First, connect your computer to the Wi-Fi network of the Tello drone.
   Execute the following script to start the initial color filtering process:
   ```sh
   python extra_files/color_filter.py

2. After running the script, open the config file and fine-tune the HSV filter parameters based on your environment and lighting conditions.

   To run the gate traversal code, you can use the following command:
   ```sh
   python gate_follower/main.py

3. To run the line follower code, you can use the following command:
   ```sh
   python line_folower/main_wline.py
   
## Fake Tello
If you don't have access to a Tello drone or can't run the code with the actual device, you can use the [FakeTello](./fake_tello.py) module instead of djitellopy to test and run the code without a drone.


## Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

- Fork the Project
- Create your Feature Branch (git checkout -b feature/AmazingFeature)
- Commit your Changes (git commit -m 'Add some AmazingFeature')
- Push to the Branch (git push origin feature/AmazingFeature)
- Open a Pull Request

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](./LICENSE) file for details.

## Contact
Zahra Babaei - [LinkedIn](https://www.linkedin.com/in/zahra-babaei-21a5a5282/) - [Email](Z.babaiy290@gmail.com)

Zahra Mazinani - [LinkedIn](https://www.linkedin.com/in/zahramazinani/) - [Email](mazinani.zh@gmail.com)

Project Link: https://github.com/Zahra-Mazinani/FiraAirPro2025
