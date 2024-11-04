import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt

class VolumeVisualizer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setFixedSize(400, 200)
        self.draw_volume_bar(50)  # 초기 볼륨 레벨을 50으로 설정

    def draw_volume_bar(self, level):
        self.scene.clear()
        bar_height = level * 2  # 볼륨 레벨에 따라 바 높이 결정
        self.scene.addRect(50, 200 - bar_height, 100, bar_height, Qt.blue, Qt.blue)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    visualizer = VolumeVisualizer()
    visualizer.show()
    visualizer.draw_volume_bar(75)  # 예시로 볼륨 레벨을 75로 업데이트
    sys.exit(app.exec_())