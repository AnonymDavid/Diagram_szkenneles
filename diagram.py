import numpy as np
import cv2

# read, make it black and white
img = cv2.imread("tests/test3.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

kernel = np.ones((3, 3), np.uint8) 

# making lines stronger for easier recognition
eroded = cv2.erode(thresh, kernel)

# finding areas
num_labels, labels_im = cv2.connectedComponents(eroded)

areas = []

for label in range(1,num_labels):
    # create mask from area
    mask = np.zeros((img.shape[0],img.shape[1]), dtype=np.uint8)
    mask[labels_im == label] = 255
    
    # find contours in mask
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cnt = contours[0]
    
    # figuring out shapes
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    
    x, y, w, h = cv2.boundingRect(approx)
    
    if len(approx) == 3:
        # triangle
        areas.append([[x,y,w,h],'T'])
    elif len(approx) == 4:
        # quadrangle
        if 1 - (cv2.contourArea(cnt) / (w*h)) <= 0.05:
            # rectangle
            areas.append([[x,y,w,h],'R'])
        elif abs(1 - (2 * cv2.contourArea(cnt) / (w*h))) <= 0.05:
            # diamond
            areas.append([[x,y,w,h],'D'])
        else:
            # parallelogram
            areas.append([[x,y,w,h],'P'])
    elif len(approx) > 4:
        # elipse
        areas.append([[x,y,w,h],'E'])
    
    # if two areas overlap, delete the bigger (filter out ares where components and lines enclosed an area)
    for i in range(len(areas) - 1):
        if (x <= areas[i][0][0]+areas[i][0][2]) and (y <= areas[i][0][1]+areas[i][0][3]) and (x+w >= areas[i][0][0]) and (y+h >= areas[i][0][1]):
            if (w*h < areas[i][0][2]*areas[i][0][3]):
                del(areas[i])
            else:
                del(areas[-1])
            break

for area in areas:
    cv2.rectangle(img, (area[0][0],area[0][1]), (area[0][0]+area[0][2],area[0][1]+area[0][3]), (255,0,255), 3)
    cv2.putText(img, str(area[1]), (area[0][0]+10,area[0][1]+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)


# creating xml file for draw.io
file = open('output.xml','w')

file.write('<mxGraphModel dx="200" dy="200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="400" pageHeight="400" math="0" shadow="0">\n<root>\n')

file.write('<mxCell id="0" />\n<mxCell id="1" parent="0" />\n')

id = 2

for area in areas:
    if area[1] == 'T':
        # triangle
        file.write('<mxCell id="'+str(id)+'" value="" style="triangle;whiteSpace=wrap;html=1;" vertex="1" parent="1">\n<mxGeometry x="'+str(area[0][0])+'" y="'+str(area[0][1])+'" width="'+str(area[0][2])+'" height="'+str(area[0][3])+'" as="geometry" />\n</mxCell>\n')
    elif area[1] == 'R':
        # rectangle
        file.write('<mxCell id="'+str(id)+'" value="" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">\n<mxGeometry x="'+str(area[0][0])+'" y="'+str(area[0][1])+'" width="'+str(area[0][2])+'" height="'+str(area[0][3])+'" as="geometry" />\n</mxCell>\n')
    elif area[1] == 'D':
        # diamond
        file.write('<mxCell id="'+str(id)+'" value="" style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1">\n<mxGeometry x="'+str(area[0][0])+'" y="'+str(area[0][1])+'" width="'+str(area[0][2])+'" height="'+str(area[0][3])+'" as="geometry" />\n</mxCell>\n')
    elif area[1] == 'P':
        # parallelogram
        file.write('<mxCell id="'+str(id)+'" value="" style="shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;" vertex="1" parent="1">\n<mxGeometry x="'+str(area[0][0])+'" y="'+str(area[0][1])+'" width="'+str(area[0][2])+'" height="'+str(area[0][3])+'" as="geometry" />\n</mxCell>\n')
    else:
        # elipse
        file.write('<mxCell id="'+str(id)+'" value="" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">\n<mxGeometry x="'+str(area[0][0])+'" y="'+str(area[0][1])+'" width="'+str(area[0][2])+'" height="'+str(area[0][3])+'" as="geometry" />\n</mxCell>\n')
    
    id += 1

file.write('</root>\n</mxGraphModel>\n')

file.close()

cv2.imshow("img", img)
cv2.waitKey()
cv2.destroyAllWindows()

