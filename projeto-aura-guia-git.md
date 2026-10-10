# Projeto Aura — Guia de Git e GitHub (passo a passo)

> Para levar o código do Aion do **notebook** (Windows, onde ele é escrito) para o **PC Aura** (Debian, onde ele roda), usando o GitHub como "ponto de encontro" entre os dois.
> Siga um passo de cada vez e só avance quando o resultado na tela for o esperado. Se algo der diferente, pare e peça ajuda com o que apareceu na tela.

Cada bloco é marcado com **onde** deve ser executado:

- **[NOTEBOOK]** → Prompt de Comando (CMD) do Windows
- **[SITE]** → no navegador, em github.com
- **[PC AURA]** → terminal do Debian

---

## Vocabulário mínimo

| Palavra | O que significa |
|---|---|
| **Repositório** | A pasta do projeto, com todo o histórico de mudanças guardado. |
| **Commit** | Uma "foto" do projeto num momento, com uma mensagem explicando o que mudou. |
| **Push** | Enviar os commits do computador para o GitHub. |
| **Pull** | Trazer do GitHub os commits que este computador ainda não tem. |
| **Clone** | Copiar um repositório do GitHub para um computador pela primeira vez. |
| **Token** | Uma "senha especial", gerada no GitHub, usada no lugar da senha da conta. |

**Princípio de trabalho:** o código é **escrito no notebook** e só **executado no PC Aura**. O fluxo é sempre: notebook → GitHub → PC Aura.

---

## DECISÃO PRÉVIA: repositório público ou privado?

Existe um detalhe prático: **o terminal do Debian não permite copiar e colar**. Num repositório **privado**, o PC Aura precisa de um token (cerca de 90 caracteres) que teria de ser **digitado à mão**.

| | Público | Privado |
|---|---|---|
| Quem vê o código | Qualquer pessoa na internet | Só você |
| PC Aura precisa de token? | **Não** (clone e pull livres) | **Sim**, digitado à mão (ou via SSH, ver apêndice) |
| Dificuldade | Menor | Maior |

**Sugestão para começar:** público, pela simplicidade. A visibilidade pode ser mudada a qualquer momento nas configurações do repositório.

**Regra de ouro (vale nos dois casos):** nunca coloque no código senhas, tokens ou chaves de API (por exemplo, a chave da IA que o Aion usará no futuro). Isso fica sempre fora do repositório.

---

# PARTE A — Preparar o notebook

## A1. Conferir que o Git está instalado — [NOTEBOOK]

```
git --version
```
Deve aparecer algo como `git version 2.xx.x`.

## A2. Conferir sua identidade — [NOTEBOOK]

```
git config --global --list
```
Procure as linhas `user.name=` e `user.email=`. Se já existirem, pule para A3. Se não existirem:

```
git config --global user.name "Seu Nome"
git config --global user.email "seu-email"
```

**Dica de privacidade:** esse e-mail fica gravado em cada commit (e visível, se o repositório for público). O GitHub oferece um e-mail "noreply" (algo como `12345678+usuario@users.noreply.github.com`), que aparece em **Settings → Emails**. Você pode usar esse.

## A3. Criar o repositório no GitHub — [SITE]

1. Entre em github.com e clique no **+** (canto superior direito) → **New repository**.
2. **Repository name:** `projeto-aura`
3. Escolha **Public** ou **Private** (ver decisão acima).
4. **Muito importante:** deixe **desmarcadas** as opções "Add a README file", "Add .gitignore" e "Choose a license". O repositório precisa nascer **vazio**, porque vamos enviar uma pasta que já existe.
5. Clique em **Create repository**.
6. Na página que abrir, copie o endereço HTTPS, parecido com:
   `https://github.com/SEU_USUARIO/projeto-aura.git`

## A4. Entrar na pasta do projeto — [NOTEBOOK]

```
cd %USERPROFILE%\Documents\ProjetoAura
git status
```

- Se aparecer `On branch ...`, a pasta já é um repositório: siga para A5.
- Se aparecer `fatal: not a git repository`, rode:
  ```
  git init
  ```

## A5. Dizer ao Git o que NÃO deve guardar — [NOTEBOOK]

A pasta `aura-env` (o ambiente virtual do Python) é grande e específica deste computador; não deve ir para o GitHub. Crie o arquivo `.gitignore`:

```
echo aura-env/> .gitignore
echo __pycache__/>> .gitignore
echo *.pyc>> .gitignore
```

Conferir:
```
type .gitignore
```
Devem aparecer as três linhas: `aura-env/`, `__pycache__/` e `*.pyc`.

## A6. Ver o que será guardado — [NOTEBOOK]

```
git add .
git status
```

Confira a lista "Changes to be committed": deve conter seus arquivos `.py` e o `.gitignore`. **A pasta `aura-env` NÃO deve aparecer.** Se aparecer, pare e peça ajuda.

> Avisos como "LF will be replaced by CRLF" são normais no Windows. Pode ignorar.

## A7. Primeiro commit — [NOTEBOOK]

```
git commit -m "Primeira versao do Projeto Aura"
```
Se aparecer `Author identity unknown`, volte ao passo A2.

## A8. Nome do ramo principal — [NOTEBOOK]

```
git branch -M main
```
(O GitHub usa o nome `main`; o Git do Windows pode ter criado como `master`. Este comando acerta.)

## A9. Ligar a pasta ao repositório do GitHub — [NOTEBOOK]

Troque `SEU_USUARIO` pelo seu nome de usuário do GitHub:

```
git remote add origin https://github.com/SEU_USUARIO/projeto-aura.git
git remote -v
```
O segundo comando deve mostrar o endereço duas vezes (`fetch` e `push`).

## A10. Enviar para o GitHub — [NOTEBOOK]

```
git push -u origin main
```

Na primeira vez, pode abrir uma janela do navegador pedindo para você entrar na conta do GitHub e autorizar: faça isso normalmente. Ao terminar, o terminal mostra algo como `branch 'main' set up to track 'origin/main'`.

**Conferir:** abra a página do repositório no GitHub (F5) e veja se seus arquivos estão lá.

---

# PARTE B — Rotina de trabalho no notebook

Sempre que fizer uma mudança que queira guardar:

```
cd %USERPROFILE%\Documents\ProjetoAura
git status
git add .
git commit -m "Descreva em uma frase o que mudou"
git push
```

Comandos úteis para olhar o histórico:

| Comando | Para que serve |
|---|---|
| `git status` | Mostra o que mudou desde o último commit |
| `git log --oneline` | Lista os commits, do mais recente ao mais antigo |
| `git diff` | Mostra as linhas alteradas, ainda não "adicionadas" |

**Dica:** faça commits pequenos e frequentes, com mensagens claras (ex.: "Ajuste da espessura da linha"). Se um ajuste der errado, fica fácil voltar atrás.

---

# PARTE C — Levar o código para o PC Aura

## C1. (Só se o repositório for PRIVADO) Criar um token de leitura — [SITE]

1. No GitHub: clique na sua foto (canto superior direito) → **Settings**.
2. Menu da esquerda, no final: **Developer settings**.
3. **Personal access tokens → Fine-grained tokens → Generate new token**.
4. **Token name:** `PC Aura (somente leitura)`
5. **Expiration:** escolha um prazo (por exemplo, 1 ano) e anote a data para renovar.
6. **Repository access:** **Only select repositories** → escolha `projeto-aura`.
7. **Permissions → Repository permissions → Contents:** **Read-only**.
8. **Generate token** e **copie o token imediatamente** (o GitHub mostra uma única vez). Guarde num lugar seguro.

> O token é uma senha: **nunca** o cole em chats, no código, nem em mensagens. Como esse é somente leitura e só enxerga um repositório, o risco é pequeno, mas o cuidado continua valendo.

## C2. Instalar o Git no Debian — [PC AURA]

```
apt update
apt install git -y
```

## C3. Baixar (clonar) o projeto — [PC AURA]

```
cd /root
git clone https://github.com/SEU_USUARIO/projeto-aura.git
```

- **Repositório público:** baixa direto, sem pedir nada.
- **Repositório privado:** pede `Username` (seu usuário do GitHub) e `Password` (cole/digite o **token**). Ao digitar a senha **nada aparece na tela**; isso é normal. Digite com atenção e aperte Enter.

Conferir:
```
cd projeto-aura
ls
```
Devem aparecer seus arquivos `.py`.

## C4. (Só repositório privado) Não precisar digitar o token toda vez — [PC AURA]

```
git config --global credential.helper store
```
Na próxima vez que o Git pedir usuário e token, ele **grava** os dados e não pergunta mais. (Ficam num arquivo de texto simples em `/root/.git-credentials`, aceitável num PC dedicado, e o token só lê.)

## C5. Atualizar o PC Aura quando houver novidades — [PC AURA]

Depois de um `git push` no notebook:

```
cd /root/projeto-aura
git pull
```

---

# PARTE D — Problemas comuns

| O que aparece | O que significa | O que fazer |
|---|---|---|
| `fatal: not a git repository` | Você não está dentro da pasta do projeto | Use `cd` para entrar na pasta certa |
| `Author identity unknown` | Faltou o nome/e-mail do Git | Passo A2 |
| `src refspec main does not match any` | Nome do ramo errado, ou ainda não houve commit | Faça o commit (A7) e depois `git branch -M main` (A8) |
| `rejected ... fetch first` (no push) | O repositório no GitHub não estava vazio (ex.: README criado no site) | Peça ajuda; há uma correção simples, mas é melhor entender o caso |
| `Authentication failed` (privado) | Token errado, expirado, ou sem permissão em "Contents" | Gere outro token (C1) e tente de novo |
| `aura-env` apareceu no `git status` | O `.gitignore` não foi criado/lido | Refaça A5; se já foi commitado: `git rm -r --cached aura-env` e commit |
| Aviso `LF will be replaced by CRLF` | Diferença de fim de linha Windows/Linux | Normal; ignore |

**Ajustes feitos direto no PC Aura:** como o fluxo é notebook → GitHub → PC Aura, uma alteração feita só no PC Aura pode conflitar no próximo `git pull`. Se precisar mexer lá, avise antes para combinarmos como guardar essa mudança.

---

# APÊNDICE (opcional) — Controlar o PC Aura pelo notebook (SSH)

Permite **copiar e colar** comandos (e o token) no PC Aura, a partir do notebook. Só funciona se os dois estiverem na mesma rede local; teste primeiro.

1. **[PC AURA]** Instalar o servidor SSH e descobrir o endereço:
   ```
   apt install openssh-server -y
   hostname -I
   ```
   Anote o primeiro número, algo como `192.168.0.25`.
2. **[NOTEBOOK]** Testar se o notebook enxerga o PC Aura:
   ```
   ping 192.168.0.25
   ```
   Se responder, siga. Se não responder (o PC Aura pode estar atrás de outro roteador/rede), este apêndice não se aplica.
3. **[NOTEBOOK]** Conectar (use o usuário criado na instalação do Debian, aqui `aion`):
   ```
   ssh aion@192.168.0.25
   ```
   Aceite a pergunta (digite `yes`) e informe a senha do usuário. Depois, para virar administrador:
   ```
   su -
   ```
   A partir daí, o que você colar na janela do CMD (botão direito) vai para o PC Aura.

---

# Cartão de referência rápida

**Notebook (depois de mexer no código):**
```
git add .
git commit -m "mensagem"
git push
```

**PC Aura (para receber a novidade):**
```
cd /root/projeto-aura
git pull
```

---
*Guia gerado por Claude para o Projeto Aura, para uso pessoal de Márlon. Não é o documento compartilhado entre as IAs.*
