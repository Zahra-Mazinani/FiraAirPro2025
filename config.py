# gate variables
gate_lower = [82,161,109]
gate_upper = [231,193,255]
threshold_x = 8 #cm
threshold_y = 8 #cm

# H_detection variables
H_template_Path = 'D:\\fira_air_2025\\codes\\H.png'

# automate color filtering 
sample_pixels_coords = [(20,20), (180,130), (180, 20), (130,20)] # می توانید این مختصات را تغییر دهید

# line_follower variables
sensors = 3
threshold = 0.2
width, height = 480, 360
senstivity = 3  # if number is high less sensitive
weights = [-25, -15, 0, 15, 25]
fSpeed = 15
curve = 0
line_lower = [82,62,66]
line_upper = [180,255,255]
