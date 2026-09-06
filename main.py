def mostrar_menu():
    print("=" * 40)
    print("             WTGPT")
    print("   War Thunder AI Assistant")
    print("=" * 40)
    print("1. Analizar vehículo")
    print("2. Comparar vehículos")
    print("3. Economía")
    print("4. Estadísticas")
    print("5. Salir")
    print("=" * 40)


def ejecutar():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            print("\n[WTGPT] Análisis de vehículos: próximamente.\n")
        elif opcion == "2":
            print("\n[WTGPT] Comparación de vehículos: próximamente.\n")
        elif opcion == "3":
            print("\n[WTGPT] Módulo de economía: próximamente.\n")
        elif opcion == "4":
            print("\n[WTGPT] Estadísticas: próximamente.\n")
        elif opcion == "5":
            print("\nWTGPT cerrado. ¡Nos vemos en el campo de batalla! 🎮")
            break
        else:
            print("\nOpción no válida. Inténtalo de nuevo.\n")


if __name__ == "__main__":
    ejecutar()
