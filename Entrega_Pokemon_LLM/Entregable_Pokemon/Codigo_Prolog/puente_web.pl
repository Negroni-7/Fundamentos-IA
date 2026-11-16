% Puente web: reutiliza opcion/5 y resp_* de chatbot.pl
%   swipl -q puente_web.pl opciones
%   swipl -q puente_web.pl consultar N Valor1 Valor2 ...
% Salida: 0 = respondio, 2 = entrada no valida
:- ensure_loaded('chatbot.pl').

:- initialization(puente, main).

puente :-
    current_prolog_flag(argv, Argv),
    argumentos_usuario(Argv, Args),
    (   Args = [opciones]
    ->  listar_opciones
    ;   Args = [consultar, TextoN | Textos]
    ->  consultar(TextoN, Textos)
    ;   writeln('Uso: swipl -q puente_web.pl opciones | consultar N [valores]'),
        halt(2)
    ).

% Segun la version de SWI-Prolog, argv puede incluir el ejecutable y el script.
argumentos_usuario(Argv, Args) :-
    (   append(_, [Cmd | Resto], Argv),
        memberchk(Cmd, [opciones, consultar])
    ->  Args = [Cmd | Resto]
    ;   Args = []
    ).

listar_opciones :-
    forall(( categoria(Cat, Titulo), opcion(N, Cat, Texto, Entradas, _) ),
           (   findall(E, ( member(Clase:Etiqueta, Entradas),
                            format(atom(E), '~w=~w', [Clase, Etiqueta]) ), Es),
               atomic_list_concat(Es, ';', TxtEntradas),
               format('~w|~w|~w|~w~n', [N, Titulo, Texto, TxtEntradas])
           )).

consultar(TextoN, Textos) :-
    (   atom_number(TextoN, N), integer(N), opcion(N, _, _, Entradas, Pred)
    ->  true
    ;   format('La opcion "~w" no existe en el menu.~n', [TextoN]),
        halt(2)
    ),
    length(Entradas, Esperados),
    length(Textos, Recibidos),
    (   Esperados =:= Recibidos
    ->  true
    ;   format('La opcion ~w necesita ~w dato(s) y se recibieron ~w.~n',
               [N, Esperados, Recibidos]),
        halt(2)
    ),
    validar_valores(Entradas, Textos, Valores),
    Meta =.. [Pred | Valores],
    (   catch(call(Meta), _, fail)
    ->  true
    ;   writeln('No se encontro una respuesta para esa consulta.')
    ).

% Misma validacion que pedir/3 del chatbot de consola: busca dentro del texto
% alguna palabra que pertenezca al dominio (acepta "el pokemon Pikachu").
validar_valores([], [], []).
validar_valores([Clase:_ | Resto], [Texto | Textos], [Valor | Valores]) :-
    palabras(Texto, Ws),
    (   member(W, Ws), existe(Clase, W)
    ->  Valor = W
    ;   format('No encontre ningun ~w valido en "~w". Revise que este registrado en la base de conocimiento.~n',
               [Clase, Texto]),
        halt(2)
    ),
    validar_valores(Resto, Textos, Valores).
