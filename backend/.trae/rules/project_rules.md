Sempre que fizermos uma atualização em alguma tabela, coluna, rls, etc, temos que atualizar o db_setup.sql.

nós verificamos antes de alterar coisas que já existem se elas estão corretamente configuradas.

Então para cada tabela, coluna, rls, etc. Vamos primeiro verificar se já temos, se não tivermos alteramos, se tivermos mantemos, se tivermos mas não da forma certa alteramos.

Temos que garantir que o script sempre atualize tudo no supa sem quebrar nada que já tinhamos anteriormente


Sempre consulte o product_prd.md para verificar se as alterações estão de acordo com o que foi planejado. Caso precisemos sair do planejamento, temos que atualizar o product_prd.md também. Caso precisemos fazer alguma alteração no product_prd.md, temos que fazer antes de atualizar o db_setup.sql