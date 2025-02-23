# TrackerPrinter

Um script Python para capturar screenshots de perfis de usuários em trackers torrent de forma automatizada, usando o Selenium WebDriver. Ideal para arquivar ou monitorar informações de perfis em trackers privados ou públicos.

## Funcionalidades
- Captura screenshots da viewport visível (`visible`) ou da página completa (`full`) em modo headless.
- Suporta login manual em trackers que exigem autenticação.
- Configuração flexível via arquivo `trackers.conf` com trackers padrão definidos pelo usuário.
- Salvamento organizado dos screenshots com timestamp, tracker e nome do usuário no nome do arquivo.

## Pré-requisitos
- **Python**: Versão 3.6 ou superior.
- **Dependências Python**: `selenium` (`pip3 install selenium`).
- **ChromeDriver**: Baixe o ChromeDriver compatível com sua versão do Google Chrome de [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads). Adicione ao PATH ou coloque no diretório do script.

## Instalação
1. Clone o repositório: `git clone https://github.com/seu_usuario/trackerprinter.git && cd trackerprinter`
2. Instale as dependências: `pip3 install selenium`
3. Configure o ChromeDriver:
   - **Linux**: `sudo mv chromedriver /usr/local/bin/ && sudo chmod +x /usr/local/bin/chromedriver`
   - **Windows**: Adicione o diretório do `chromedriver.exe` ao PATH ou coloque-o na pasta do script.

## Configuração
O script utiliza um arquivo `trackers.conf` para definir os trackers e usuários a processar. Um modelo é fornecido em `template.trackers.conf`.
1. Copie o template: `cp template.trackers.conf trackers.conf`
2. Edite `trackers.conf`:
   - Atualize a linha `default_trackers` na seção `[TRACKERS]` com os trackers que deseja processar.
   - Preencha os `users` nas seções correspondentes com os nomes de usuário reais.
   - Exemplo:
     ```
     [TRACKERS]
     default_trackers = CBR, TL

     [CBR]
     base_url = https://capybarabr.com/users/
     users = franzopl, joaozinho, maria

     [TL]
     base_url = https://www.torrentleech.org/profile/
     users = franzopl, joaozinho, maria
     ```

## Uso
Execute o script com os seguintes comandos:
- **Captura apenas visível (padrão)**: `python3 main.py`
- **Captura apenas completa**: `python3 main.py --full`
- **Especificar trackers manualmente**: `python3 main.py --full --tk CBR TL`
- **Personalizar timeout e diretório de saída**: `python3 main.py --full --timeout 10 --output-dir myscreenshots`

### Opções de linha de comando
- `--full`: Captura apenas a página completa (headless).
- `--tk <tracker1> <tracker2>`: Especifica trackers a processar, sobrescrevendo `default_trackers`.
- `--timeout <segundos>`: Define o tempo de espera para carregamento da página (padrão: 5).
- `--output-dir <diretório>`: Define o diretório de saída para os screenshots (padrão: `screenshots`).

## Exemplo de Configuração e Execução
1. Edite `trackers.conf`:
   [TRACKERS]
   default_trackers = CBR, TL
   [CBR]
   base_url = https://capybarabr.com/users/
   users = franzopl
   [TL]
   base_url = https://www.torrentleech.org/profile/
   users = franzopl
2. Execute: `python3 main.py --full`
Saída esperada:
 Processando CBR...
   INFO - Não detectada tela de login em https://capybarabr.com/users/franzopl
   CBR não requer login, prosseguindo com capturas.
   Acessando perfil: https://capybarabr.com/users/franzopl
   Screenshot completo salvo em: screenshots/20250222_123456_CBR_franzopl_full.png
   Processando TL...
   INFO - Detectada tela de login em https://www.torrentleech.org/profile/franzopl com //input[@type='password']
   TL requer login.
   Por favor, faça login manualmente no TL em https://www.torrentleech.org/profile/franzopl
   [espera login]
   Screenshot completo salvo em: screenshots/20250222_123457_TL_franzopl_full.png


## Notas
- **Login**: Para trackers que exigem autenticação, o script abrirá o navegador para login manual e usará os cookies salvos no perfil do Chrome (`~/.chrome_torrent_profile` no Linux, `%USERPROFILE%\.chrome_torrent_profile` no Windows).
- **Trackers privados**: Certifique-se de ter acesso aos trackers listados em `trackers.conf`.

## Contribuição
1. Faça um fork do repositório.
2. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -am 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato
Para sugestões ou problemas, abra uma issue no repositório.