# SGA - Sistema de Gestão de Artigos

**SGA** (Sistema de Gestão de Artigos) é uma aplicação web desenvolvida com o framework Flask, projetada para facilitar a gestão de artigos científicos de forma eficiente. O sistema permite o cadastro, listagem e análise detalhada de dados dos artigos, oferecendo métricas importantes por meio de dashboards interativos. Além disso, possibilita a geração de relatórios completos em PDF. O SGA também conta com um robusto sistema de gerenciamento de usuários, com níveis de permissão diferenciados, garantindo que administradores possam gerenciar e controlar o acesso ao sistema de maneira segura e eficaz.

## Funcionalidades Principais

### 1. Autenticação e Controle de Acesso
- **Login e Logout**: Usuários podem se autenticar no sistema.
- **Controle de Acesso**: Diferenciação de permissões entre usuários comuns e administradores.
- **Administração**: Administradores têm acesso a funcionalidades exclusivas, como o gerenciamento e cadastro de usuários.

### 2. Cadastro de Artigos
- **Formulário de Cadastro**: Submissão de artigos com informações detalhadas como título, ano, autores, classificação Qualis, ISSN, e fator de impacto.
- **Validação de Formulário**: Mensagens de erro são exibidas em caso de campos inválidos.

### 3. Listagem de Artigos
- **Tabela de Artigos**: Visualização de todos os artigos cadastrados no sistema.
- **Exportação de Dados**: Em breve, será possível exportar a listagem de artigos para **CSV** e **JSON**.

### 4. Dashboard Analítico
- **Análise de Dados**: Dashboard que exibe gráficos e métricas principais dos artigos, incluindo total de artigos, média de fator de impacto e distribuição por ano e classificação Qualis.
- **Gráficos Interativos**: Utiliza **Chart.js** para gráficos de linha, barra e pizza.

### 5. Geração de Relatórios em PDF
- **Relatórios em PDF**: Geração de relatórios com gráficos e dados diretamente do dashboard, utilizando **ReportLab** gerar o PDF.

### 6. Gestão de Usuários
- **Listagem de Usuários**: Administradores podem visualizar e gerenciar os usuários cadastrados.
- **Cadastro de Novos Usuários**: Administradores podem adicionar novos usuários via um formulário dedicado.
- **Ações de Administração**: Redefinir senhas e excluir usuários.

### 7. Feedback Visual com Toastr
- **Mensagens Dinâmicas**: Toastr é usado para exibir notificações de sucesso, erro, ou informações, criando uma experiência mais fluida para o usuário.

---

## Instalação


## Como Usar

### Cadastro de Usuários
- **Usuários comuns** podem se registrados diretamente por um usuário admin do sistema.
- **Administradores** têm controle completo sobre o sistema, podendo cadastrar, editar e remover usuários e artigos.

### Geração de Relatórios
- Acesse o **dashboard** e clique no botão **"Baixar Relatório em PDF"** para gerar relatórios com gráficos e métricas principais.

### Administração de Usuários
- No menu de administração, gerencie usuários com opções para redefinir senhas e excluir contas.

---

## Tecnologias Utilizadas

- **Flask**: Framework principal para o desenvolvimento da aplicação web.
- **TailwindCSS**: Utilizado para estilização moderna e responsiva.
- **Plotly**: Gráficos para gerar relatórios de análise de dados no dashboard.
- **Chart.js**: Gráficos interativos para análise de dados no dashboard.
- **Toastr**: Notificações dinâmicas para feedback visual.
- **SQLite**: Banco de dados padrão para armazenamento dos dados (pode ser substituído por outro banco de dados relacional).

---

## Telas do Sistema de Gestão de Artigos

Aqui estão prévias das telas principais do SGA:

![Painel do Sistema](/assets/img/painel.png)  <!-- Substitua o caminho para o arquivo de imagem correto -->

![Dashboard](/assets/img/dashboard.png)  <!-- Substitua o caminho para o arquivo de imagem correto -->
![Gerenciamento de Artigos](/assets/img/gerenciamento.png)  <!-- Substitua o caminho para o arquivo de imagem correto -->
![Formulário](/assets/img/formulario_cadastro.png)  <!-- Substitua o caminho para o arquivo de imagem correto -->

---

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir **issues** ou enviar **pull requests**.

---

## Licença

Este projeto está licenciado sob a **MIT License**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

