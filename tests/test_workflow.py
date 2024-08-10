
def test_app():
    # agree EULA (neutralized to prevent fail)
    #with open("eula.txt", "w") as ef:
    #  ef.write("eula=true")

    #start the server
    import os
    os.system("python main.py")
