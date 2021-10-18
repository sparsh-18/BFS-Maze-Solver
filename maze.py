import cv2
import threading

# A class to store the x and y coordinate of a point
# The + and = operators are overloaded to work for it
class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


mouse_click_status = 0
# a flag variable to store status of mouse clicks.
# 0 -> no clicks
# 1 -> first click (start)
# 2 -> second click (end)


rw = 4  # for position of the rectangle drawn on image when clicked

start = Point()  # starting point
end = Point()  # ending point

# directions of surrounding nodes for BFS
directions = [Point(0, -1), Point(0, 1), Point(1, 0), Point(-1, 0)]


# The BFS function:
# All the pixels surrounding the starting pixel acts as neighbouring nodes
# Breadth First Search is performed until the ending point is found
def bfs(s, e):

    global img, h, w

    # ending point found
    found = False

    # queue to perform BFS
    queue = []

    # visited matrix of size width*height of the image with each element = 0
    visited = [[0 for j in range(w)] for i in range(h)]

    # parent matrix of size width*height of the image with each element = empty Point object
    parent = [[Point() for j in range(w)] for i in range(h)]

    # storing starting Point and marking it 1 in visited matrix
    queue.append(s)
    visited[s.y][s.x] = 1

    # looping until queue is not empty
    while len(queue) > 0:
        # popping one element from queue and storing in p
        p = queue.pop(0)

        # surrounding elements
        for d in directions:
            cell = p + d

            # if cell(a surrounding pixel) is in range of image, not visited, !(B==0 && G==0 && R==0) i.e. pixel is
            # not black as black represents border
            if (0 <= cell.x < w and 0 <= cell.y < h and
            visited[cell.y][cell.x] == 0 and
                    (img[cell.y][cell.x][0] != 0 or img[cell.y][cell.x][1] != 0 or img[cell.y][cell.x][2] != 0)):

                queue.append(cell)

                # marking cell as visited
                visited[cell.y][cell.x] = 1
                # changing the pixel color to red
                img[cell.y][cell.x] = [0, 0, 255]

                # string the value of p in parent matrix to trace path
                parent[cell.y][cell.x] = p

                # if end is found break
                if cell == e:
                    found = True
                    del queue[:]
                    break

    # list to trace path
    path = []
    if found:
        p = e

        while p != s:
            path.append(p)
            p = parent[p.y][p.x]

        path.append(p)
        path.reverse()

        # changing the pixel of resulting path to white
        for p in path:
            img[p.y][p.x] = [255, 255, 255]


def mouse_click(event, px, py, flag, params):

    global img, mouse_click_status, start, end, rw

    # if left clicked
    if event == cv2.EVENT_LBUTTONUP:
        # first click
        if mouse_click_status == 0:
            # create a rectangle on the image
            cv2.rectangle(img, (px-rw, py-rw), (px+rw, py+rw), (0, 0, 255), -1)
            # store the starting point
            start = Point(px, py)
            # change status to 1
            mouse_click_status = mouse_click_status + 1

        # second click
        elif mouse_click_status == 1:
            # create a rectangle on the image
            cv2.rectangle(img, (px-rw, py-rw), (px+rw, py+rw), (0, 255, 255), -1)
            # store the ending point
            end = Point(px, py)
            # change status to 2
            mouse_click_status = mouse_click_status + 1

# display function
def display():
    global img
    cv2.imshow("image", img)
    cv2.setMouseCallback("image", mouse_click)
    while True:
        cv2.imshow("image", img)
        cv2.waitKey(1)


# reading the image
img = cv2.imread("maze.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# resizing the image
img = cv2.resize(img, (1080, 720), interpolation=cv2.INTER_NEAREST)

_, img = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
# img object, threshold value, color of threshold, Binary thresh because 2 colors

img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

# height and width of image
h, w = img.shape[:2]

# thread to run the display function simultaneously
t = threading.Thread(target=display, args=())
t.daemon = True
t.start()

# Preventing BFS function to run until both clicks are performed and the starting and ending point are stored
while mouse_click_status < 2:
    pass

# calling BFS function
bfs(start, end)

cv2.waitKey(0)
