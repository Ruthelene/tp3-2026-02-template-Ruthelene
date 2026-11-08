"""T10 - Indice descendente: repete o T9 com v DESC NULLS FIRST e fillfactors [100] + individuais."""
from params import carregar
from t09_fillfactor import rodar


def main():
    rodar(" DESC NULLS FIRST", [100] + carregar()["fillfactors"], "t10")


if __name__ == "__main__":
    main()