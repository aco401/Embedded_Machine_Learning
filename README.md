# Embedded_Machine_Learning

Projekt in dem Modul "Embedded Machine Learning"

## Abstract (siehe Ausarbeitung.pdf)
In dieser Ausarbeitung wird eine Anwendung
beschrieben, die die Vermeidung einer krummen Sitzposi-
tion und einer Ablenkung durch das Smartphone verbessert.
Des Weiteren strebt die Anwendung eine Verbesserung des
regelmäßigen Lüftens und der regelmäßigen Flüssigkeitszu-
nahme beim Arbeiten mit dem Computer an. Das Ziel war
es die Anwendung auf einem Raspberry Pi laufen zu lassen,
der dabei als Sensor eine Kamera und als Aktor einen Laut-
sprecher besitzt. Das, für die Erkennung der krummen Sitzpo-
sition und des Smartphones, verwendete Convolutional Neu-
ronal Net (CNN) wird dabei auf einem Coral USB Accelera-
tor inferiert. Das CNN, welches 312.712 trainierbare Param-
eter besitzt, wurde von Grund auf selbst trainiert. Für das
Training des Neuronalen Netzes und für das Funktionieren der
Anwendung bei vielen verschiedenen Kleidungen ist lediglich
ein Bilderdatensatz nötig, der mit nur einer Kleidungsmontur
aufgenommen und zu Grauwertbildern konvertiert wurde.