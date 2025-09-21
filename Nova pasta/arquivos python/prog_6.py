tarefas = []

while True:
    print("\n1 - Adicionar tarefa")
    print("2 - Ver tarefas")
    print("3 - Sair")

    opcao = input("Escolha: ")

    if opcao == "1":
        tarefa = input("Digite a tarefa: ")
        tarefas.append(tarefa)
    elif opcao == "2":
        for i, t in enumerate(tarefas, 1):
            print(f"{i}. {t}")
    elif opcao == "3":
        break
