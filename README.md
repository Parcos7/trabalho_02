### Decisões de Arquitetura e Refatoração

Durante o desenvolvimento deste sistema de inventário de ativos e vulnerabilidades, o código-fonte passou por uma etapa de refatoração. O processo teve como objetivo aprimorar a estrutura interna do projeto, sem alterar sua funcionalidade ou o comportamento externo da aplicação.

As principais decisões de engenharia de software adotadas foram:

* **Modularização e Alta Coesão:** O código Python foi reestruturado e dividido em módulos distintos para separar as responsabilidades. Essa abordagem busca garantir que cada componente apresente alta coesão, resultando em um software mais fácil de integrar, testar e manter.
* **Controle e Prevenção de Bugs:** A reorganização disciplinada do código e do fluxo de persistência de dados em arquivos JSON ajuda a simplificar o projeto interno e minimiza significativamente as chances de introdução de *bugs*.
* **Automação e Ferramental:** Para garantir a integridade do código durante a limpeza, técnicas modernas foram adotadas na IDE (como atalhos de substituição de símbolos). Isso permitiu a renomeação segura de variáveis globais e locais, como a `lista_vulns`, alterando todas as referências automaticamente e evitando efeitos colaterais indesejados.
