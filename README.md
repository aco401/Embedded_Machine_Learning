# Embedded_Machine_Learning

Projekt in dem Modul "Embedded Machine Learning"

## Abstract (siehe Ausarbeitung.pdf)
In dieser Ausarbeitung wird eine Anwendung
beschrieben, die die Vermeidung einer krummen Sitzposition 
und einer Ablenkung durch das Smartphone verbessert.
Des Weiteren strebt die Anwendung eine Verbesserung des
regelmäßigen Lüftens und der regelmäßigen Flüssigkeitszunahme
beim Arbeiten mit dem Computer an. Das Ziel war
es die Anwendung auf einem Raspberry Pi laufen zu lassen,
der dabei als Sensor eine Kamera und als Aktor einen Lautsprecher besitzt. 
Das, für die Erkennung der krummen Sitzposition und 
des Smartphones, verwendete Convolutional Neuronal Net (CNN) 
wird dabei auf einem Coral USB Accelerator inferiert. Das CNN, welches 312.712 
trainierbare Parameter besitzt, wurde von Grund auf selbst trainiert. Für das
Training des Neuronalen Netzes und für das Funktionieren der
Anwendung bei vielen verschiedenen Kleidungen ist lediglich
ein Bilderdatensatz nötig, der mit nur einer Kleidungsmontur
aufgenommen und zu Grauwertbildern konvertiert wurde.