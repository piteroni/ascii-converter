import sys
import cv2
import numpy as np

class Converter:
    def __init__(self, loadfn: str, size: int) -> None:
        tmp = cv2.imread(loadfn)
        tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2RGB)

        self.cols = size
        self.rows = np.round(size / 2 / tmp.shape[0] * tmp.shape[1]).astype(int)
        self.data = cv2.resize(tmp, (self.cols, self.rows))

    def mask_background(self, bgcolor, lower=0, upper=0) -> list:
        mask = cv2.inRange(self.data, bgcolor - lower, bgcolor + upper)
        mask = cv2.bitwise_not(mask, mask)
        self.data = cv2.bitwise_and(self.data, self.data, mask=mask)

    def get_background_color(self) -> list:
        gray = cv2.cvtColor(self.data, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 10, 100)
        edges = cv2.dilate(edges, None)
        edges = cv2.erode(edges, None)
        contour_info = []
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in contours:
            contour_info.append((
                c,
                cv2.isContourConvex(c),
                cv2.contourArea(c),
            ))
        contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
        max_contour = contour_info[0]
        mask = np.zeros(edges.shape)
        cv2.fillConvexPoly(mask, max_contour[0], (255))
        return self.data[mask == 0][0]
        
    def to_base6(self) -> list:
        colors = []
        for pixel in self.data:
            for rgb in pixel:
                rgb = np.array([np.round(5 * c / 255).astype(int) for c in rgb])
                color = int(''.join(rgb.astype(str)), 6) + 16
                colors.append(color)
        return colors
        
    def to_escape_sequences(self, colors: list) -> str:
        sequences = []
        for key, color in enumerate(colors):
            if key != 0 and key % self.cols == 0:
                sequences.append('\n')
            sequences.append('\e[38;5;{}m*\e[m'.format(color))
        return ''.join(sequences) + '\n'

if __name__ == '__main__':
    converter = Converter(sys.argv[1], 150)
    bgcolor = converter.get_background_color()
    converter.mask_background(bgcolor, 5, 2)
    colors = converter.to_base6()
    sequences = converter.to_escape_sequences(colors)
    print(sequences)
