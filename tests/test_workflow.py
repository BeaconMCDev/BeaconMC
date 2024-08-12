def test_app():
    # check if eula is not accepted in the build, to prevent starting the server without accepting it.
    with open("eula.txt", "r") as eula_file:
        eula = eula_file.read().split()
        if "eula=true" in eula:
            raise RuntimeError("Eula is accepted by default, change eula to false in eula.txt to continue.")

    # agree EULA (neutralized to prevent fail)
    # with open("eula.txt", "w") as ef:
    #  ef.write("eula=true")

    # start the server
    import os
    os.system("python main.py")
