import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.exceptions import LoginInvalidoError, SenhaInvalidaError
from entity.responsavel_familiar import ResponsavelFamiliar
from entity.validador_usuario import ValidadorUsuario


class ValidarLoginTest(unittest.TestCase):
    def test_deve_aceitar_login_valido(self):
        ValidadorUsuario.validar_login("joao")

    def test_deve_lancar_erro_quando_login_vazio(self):
        with self.assertRaises(LoginInvalidoError):
            ValidadorUsuario.validar_login("")

    def test_deve_lancar_erro_quando_login_apenas_espacos(self):
        with self.assertRaises(LoginInvalidoError):
            ValidadorUsuario.validar_login("   ")

    def test_deve_lancar_erro_quando_login_excede_tamanho_maximo(self):
        with self.assertRaises(LoginInvalidoError):
            ValidadorUsuario.validar_login("a" * 13)

    def test_deve_lancar_erro_quando_login_contem_numeros(self):
        with self.assertRaises(LoginInvalidoError):
            ValidadorUsuario.validar_login("joao1")


class ValidarSenhaTest(unittest.TestCase):
    IDENTIFICADORES = ("joao", "Joao Silva", "joao@email.com")

    def test_deve_aceitar_senha_valida(self):
        ValidadorUsuario.validar_senha("SenhaForte1", self.IDENTIFICADORES)

    def test_deve_aceitar_senha_sem_maiuscula_com_simbolo(self):
        ValidadorUsuario.validar_senha("senhaforte1!", self.IDENTIFICADORES)

    def test_deve_lancar_erro_quando_senha_muito_curta(self):
        with self.assertRaises(SenhaInvalidaError):
            ValidadorUsuario.validar_senha("Ab1", self.IDENTIFICADORES)

    def test_deve_lancar_erro_quando_senha_excede_tamanho_maximo(self):
        with self.assertRaises(SenhaInvalidaError):
            ValidadorUsuario.validar_senha("Aa1" + "a" * 126, self.IDENTIFICADORES)

    def test_deve_lancar_erro_quando_senha_tem_menos_de_tres_tipos(self):
        with self.assertRaises(SenhaInvalidaError):
            ValidadorUsuario.validar_senha("apenasminusculas", self.IDENTIFICADORES)

    def test_deve_lancar_erro_quando_senha_identica_a_identificador(self):
        senha_forte = "Forte@123"
        with self.assertRaises(SenhaInvalidaError):
            ValidadorUsuario.validar_senha(senha_forte, ("login", "nome", senha_forte))


class CriarUsuarioTest(unittest.TestCase):
    def _criar(self, login="joao", senha="SenhaForte1"):
        return ResponsavelFamiliar(
            nome="Joao Silva",
            login=login,
            email="joao@email.com",
            senha=senha,
            parentesco_principal="Pai",
        )

    def test_deve_criar_responsavel_com_dados_validos(self):
        usuario = self._criar()
        self.assertEqual(usuario.login, "joao")

    def test_deve_lancar_erro_ao_criar_usuario_com_login_invalido(self):
        with self.assertRaises(LoginInvalidoError):
            self._criar(login="joao123")

    def test_deve_lancar_erro_ao_criar_usuario_com_senha_fraca(self):
        with self.assertRaises(SenhaInvalidaError):
            self._criar(senha="fraca")


if __name__ == "__main__":
    unittest.main()
