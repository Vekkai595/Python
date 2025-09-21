import time

segundos = int(input("Quantos segundos? "))
for i in range(segundos, 0, -1):
    print(i)
    time.sleep(1)
print("⏰ Tempo acabou!")
