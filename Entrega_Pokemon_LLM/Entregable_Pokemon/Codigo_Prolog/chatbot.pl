% Conecta la base de conocimiento con el chatbot
:- ensure_loaded('base_conocimiento.pl').

categoria(tipos, 'TIPOS').
categoria(ventajas, 'VENTAJAS').
categoria(resistencias, 'RESISTENCIAS').
categoria(inmunidades, 'INMUNIDADES').
categoria(evoluciones, 'EVOLUCIONES').
categoria(consultas, 'CONSULTAS').


opcion( 1, tipos, 'De que tipo(s) es un pokemon?',
        [pokemon:'el pokemon'], resp_tipos_de).
opcion( 2, tipos, 'Que pokemon son de cierto tipo?',
        [tipo:'el tipo'], resp_pokemon_de_tipo).
opcion( 3, tipos, 'Cuantos pokemon hay de cierto tipo?',
        [tipo:'el tipo'], resp_cantidad_de_tipo).
opcion( 4, tipos, 'Un pokemon es de cierto tipo?',
        [pokemon:'el pokemon', tipo:'el tipo'], resp_es_de_tipo).
opcion( 5, tipos, 'Un pokemon tiene doble tipo?',
        [pokemon:'el pokemon'], resp_doble_tipo).

opcion( 6, ventajas, 'Que tipos son super efectivos contra un tipo?',
        [tipo:'el tipo defensor'], resp_efectivos_contra_tipo).
opcion( 7, ventajas, 'Contra que tipos es super efectivo un tipo?',
        [tipo:'el tipo atacante'], resp_efectivo_sobre).
opcion( 8, ventajas, 'Un tipo es super efectivo contra otro?',
        [tipo:'el tipo atacante', tipo:'el tipo defensor'], resp_es_efectivo).
opcion( 9, ventajas, 'Que tipos son super efectivos contra un pokemon?',
        [pokemon:'el pokemon'], resp_efectivos_contra_pokemon).

opcion(10, resistencias, 'Que tipos son resistentes a un tipo de ataque?',
        [tipo:'el tipo de ataque'], resp_resistentes_a).
opcion(11, resistencias, 'A que tipos de ataque resiste un tipo?',
        [tipo:'el tipo defensor'], resp_resiste_a).
opcion(12, resistencias, 'Un tipo resiste a otro?',
        [tipo:'el tipo defensor', tipo:'el tipo de ataque'], resp_es_resistente).

opcion(13, inmunidades, 'Que tipos son inmunes a un tipo de ataque?',
        [tipo:'el tipo de ataque'], resp_inmunes_a).
opcion(14, inmunidades, 'A que tipos de ataque es inmune un tipo?',
        [tipo:'el tipo defensor'], resp_inmune_a).
opcion(15, inmunidades, 'Un tipo es inmune a otro?',
        [tipo:'el tipo defensor', tipo:'el tipo de ataque'], resp_es_inmune).

opcion(16, evoluciones, 'A que evoluciona un pokemon?',
        [pokemon:'el pokemon'], resp_evoluciona_a).
opcion(17, evoluciones, 'Cual es la cadena evolutiva de un pokemon?',
        [pokemon:'el pokemon'], resp_cadena).
opcion(18, evoluciones, 'Es forma base o forma final?',
        [pokemon:'el pokemon'], resp_etapa).
opcion(19, evoluciones, 'Que pokemon no tienen cadena evolutiva?',
        [], resp_sin_evoluciones).
opcion(20, evoluciones, 'Dos pokemon estan en la misma cadena evolutiva?',
        [pokemon:'el primer pokemon', pokemon:'el segundo pokemon'], resp_misma_cadena).

opcion(21, consultas, 'Todos los pokemones registrados',
        [], resp_todos_los_pokemones).

opcion(22, consultas, 'Todos los tipos registrados',
        [], resp_todos_los_tipos).

%  MENU PRINCIPAL

main :-
    mostrar_menu,
    write('Elija una opcion: '),
    leer_linea(Linea),
    palabras(Linea, Ws),
    (   ( Ws == [salir] ; Ws == ['0'] )
    ->  writeln('Gracias por ocupar nuestro chat!')
    ;   Ws = [Texto], atom_number(Texto, N), integer(N),
        opcion(N, _, _, Entradas, Pred)
    ->  nl,
        ejecutar(Entradas, Pred),
        nl,
        main
    ;   writeln('Opcion no valida. Ingrese un numero del menu.'),
        main
    ).

mostrar_menu :-
    nl,
    writeln('=========================================='),
    writeln('          CHATBOT POKEMON KANTO           '),
    writeln('=========================================='),
    forall(categoria(Cat, Titulo),
           (   format('~n-- ~w --~n', [Titulo]),
               forall(opcion(N, Cat, Texto, _, _),
                      format('~t~d~3|. ~w~n', [N, Texto]))
           )),
    nl,
    writeln('  0. Salir'),
    nl.


%  INGRESO DE DATOS POR EL USUARIO

ejecutar(Entradas, Pred) :-
    (   pedir_valores(Entradas, Valores)
    ->  Meta =.. [Pred|Valores],
        call(Meta)
    ;   true
    ).


pedir_valores([], []).
pedir_valores([Clase:Etiqueta|Resto], [Valor|Valores]) :-
    pedir(Clase, Etiqueta, Valor),
    pedir_valores(Resto, Valores).


pedir(Clase, Etiqueta, Valor) :-
    format('Ingrese ~w (Enter para cancelar): ', [Etiqueta]),
    leer_linea(Linea),
    palabras(Linea, Ws),
    (   ( Ws == [] ; Ws == [salir] )
    ->  writeln('Consulta cancelada.'),
        fail
    ;   member(W, Ws), existe(Clase, W)
    ->  Valor = W
    ;   format('No encontre ningun ~w valido en "~w". Intente de nuevo.~n', [Clase, Linea]),
        pedir(Clase, Etiqueta, Valor)
    ).

existe(pokemon, X) :- es_pokemon(X).
existe(tipo, X)    :- es_tipo(X).

es_pokemon(P) :- once(tipo(P, _)).
es_tipo(T)    :- once(ventaja(T, _)).

% Normalización
palabras(Texto, Palabras) :-
    downcase_atom(Texto, Min),
    atom_chars(Min, Cs),
    maplist(limpiar_char, Cs, Cs1),
    atom_chars(Limpio, Cs1),
    atomic_list_concat(Ws0, ' ', Limpio),
    exclude(==(''), Ws0, Palabras).

limpiar_char(C, R) :-
    (   acento(C, C0) -> true ; C0 = C ),
    (   letra_o_digito(C0) -> R = C0 ; R = ' ' ).

letra_o_digito(C) :-
    char_code(C, Code),
    Code < 128,
    char_type(C, alnum).

acento('\u00e1', a).  acento('\u00e9', e).  acento('\u00ed', i).
acento('\u00f3', o).  acento('\u00fa', u).  acento('\u00fc', u).
acento('\u00f1', n).

%---------------------------------------------------------------------------------------------
lista_txt(Lista, Txt) :-
    (   Lista == []
    ->  Txt = 'ninguno'
    ;   atomic_list_concat(Lista, ', ', Txt)
    ).

leer_linea(Atom) :-
    read_line_to_string(user_input, Str),
    ( Str == end_of_file
    -> Atom = salir
    ;  atom_string(Atom, Str)
    ).
% 1
resp_tipos_de(Pokemon) :-
    tipos_de(Pokemon, ListaTipos),
    lista_txt(ListaTipos, Txt),
    format('~w es de tipo: ~w.~n', [Pokemon, Txt]).
% 2
resp_pokemon_de_tipo(Tipo) :-
    pokemon_de_tipo(Tipo, ListaPokemon),
    lista_txt(ListaPokemon, Txt),
    format('Los pokemon de tipo ~w son: ~w.~n', [Tipo, Txt]).
% 3
resp_cantidad_de_tipo(Tipo) :-
    cantidad_por_tipo(Tipo, Cantidad),
    format('Hay ~w pokemon de tipo ~w.~n', [Cantidad, Tipo]).
%4
resp_es_de_tipo(Pokemon, Tipo) :-
    (   tipos_de(Pokemon, ListaTipos), member(Tipo, ListaTipos)
    ->  format('~w es de tipo ~w.~n', [Pokemon, Tipo])
    ;   format('~w no es de tipo ~w.~n', [Pokemon, Tipo])
    ).
%5
resp_doble_tipo(Pokemon) :-
	(	doble_tipo(Pokemon)
	->	format('~w si tiene doble tipo.~n', [Pokemon])
	;	format('~w no tiene doble tipo.~n', [Pokemon])
	).
%6
resp_efectivos_contra_tipo(TipoBuscado) :-
    findall(TipoAtacante, (ventaja(TipoAtacante, Lista), member(TipoBuscado, Lista)), ListaAtacantes),
    lista_txt(ListaAtacantes, Txt),
    format('Los tipos super efectivos contra ~w son: ~w.~n', [TipoBuscado, Txt]).
%7
resp_efectivo_sobre(TipoAtacante) :-
    (   findall(TipoDefensor, (ventaja(TipoAtacante, Lista), member(TipoDefensor, Lista)), ListaDefensores)
    ->(
        lista_txt(ListaDefensores, Txt),
        format('~w es super efectivo contra: ~w.~n', [TipoAtacante, Txt])
    )
    ;   format('~w no es super efectivo contra nada.~n', [TipoAtacante])
    ).
%8
resp_es_efectivo(TipoAtacante, TipoDefensor) :-
    (   ventaja(TipoAtacante, Lista), member(TipoDefensor, Lista)
    ->  format('~w es super efectivo contra ~w.~n', [TipoAtacante, TipoDefensor])
    ;   format('~w no es super efectivo contra ~w.~n', [TipoAtacante, TipoDefensor])
    ).
%9
resp_efectivos_contra_pokemon(Pokemon) :-
    tipos_de(Pokemon, ListaTipos),
    findall(TipoAtacante, (member(TipoDefensor, ListaTipos),
                            ventaja(TipoAtacante, Lista),
                            member(TipoDefensor, Lista)),
                            ListaAtacantes),
    list_to_set(ListaAtacantes, ListaUnica),   % Eliminar duplicados
    lista_txt(ListaUnica, Txt),
    format('Los tipos super efectivos contra ~w son: ~w.~n', [Pokemon, Txt]).

%10
resp_resistentes_a(TipoBuscado) :-
    findall(TipoResistente, (resistente(TipoResistente, Lista), member(TipoBuscado, Lista)), ListaResistentes),
    lista_txt(ListaResistentes, Txt),
    format('Los tipos resistentes a ~w son: ~w.~n', [TipoBuscado, Txt]).
%11
resp_resiste_a(TipoResistente) :-
    resistente(TipoResistente, Lista),
    lista_txt(Lista, Txt),
    format('~w resiste a ~w.~n', [TipoResistente, Txt]).

%12
resp_es_resistente(TipoResistente, TipoAtacante) :-
    (   resistente(TipoResistente, Lista), member(TipoAtacante, Lista)
    ->  format('~w resiste a ~w.~n', [TipoResistente, TipoAtacante])
    ;   format('~w no resiste a ~w.~n', [TipoResistente, TipoAtacante])
    ).
%13
resp_inmunes_a(TipoBuscado) :-
    findall(TipoInmune, (inmune(TipoInmune, Lista), member(TipoBuscado, Lista)), ListaInmunes),
    lista_txt(ListaInmunes, Txt),
    format('Los tipos inmunes a ~w son: ~w.~n', [TipoBuscado, Txt]).
%14
resp_inmune_a(TipoInmune) :-
    findall(TipoAtacante, (inmune(TipoInmune, Lista), member(TipoAtacante, Lista)), ListaAtacantes),
    lista_txt(ListaAtacantes, Txt),
    format('~w es inmune a: ~w.~n', [TipoInmune, Txt]).

%15
resp_es_inmune(TipoInmune, TipoAtacante) :-
    (   inmune(TipoInmune, Lista), member(TipoAtacante, Lista)
    ->  format('~w es inmune a ~w.~n', [TipoInmune, TipoAtacante])
    ;   format('~w no es inmune a ~w.~n', [TipoInmune, TipoAtacante])
    ).
%16
resp_evoluciona_a(Pokemon) :-
    (   (evolucion([Pokemon, Evolucion|_]); evolucion([_, Pokemon, Evolucion|_]))
    ->  format('~w evoluciona a ~w.~n', [Pokemon, Evolucion])
    ;   format('~w no tiene una evolucion directa.~n', [Pokemon])
    ).
%17
resp_cadena(Pokemon) :-
    (   evolucion(Cadena), member(Pokemon, Cadena)
    ->(
          lista_txt(Cadena, Txt),
          format('La cadena evolutiva de ~w es: ~w.~n', [Pokemon, Txt])
    )
    ;   format('~w no tiene una cadena evolutiva conocida.~n', [Pokemon])
    ).
%18
resp_etapa(Pokemon) :-
    (   evolucion([Pokemon|_])
    ->  format('~w es una forma base.~n', [Pokemon])
    ;   (   evolucion(Cadena), last(Cadena, Pokemon)
        ->  format('~w es una forma final.~n', [Pokemon])
        ;   (   evolucion(Cadena), member(Pokemon, Cadena)
            ->  format('~w es una forma intermedia.~n', [Pokemon])
            ;   format('~w no tiene una cadena evolutiva conocida.~n', [Pokemon])
            )
        )
    ).
%19
resp_sin_evoluciones :-
    findall(Pokemon, (pokemon_de_tipo(_,ListaPokemones), member(Pokemon, ListaPokemones), \+ (evolucion(Cadena), member(Pokemon, Cadena))), ListaPokemon),
    list_to_set(ListaPokemon, ListaUnica),
    lista_txt(ListaUnica, Txt),
    format('Los pokemon sin evoluciones son: ~w.~n', [Txt]).
%20
resp_misma_cadena(Pokemon1, Pokemon2) :-
    (   evolucion(Cadena), member(Pokemon1, Cadena), member(Pokemon2, Cadena)
    ->  format('~w y ~w estan en la misma cadena evolutiva.~n', [Pokemon1, Pokemon2])
    ;   format('~w y ~w no estan en la misma cadena evolutiva.~n', [Pokemon1, Pokemon2])
    ).
%21
resp_todos_los_pokemones :-
    findall(Pokemon, (pokemon_de_tipo(_,ListaPokemones), member(Pokemon, ListaPokemones)), ListaPokemon),
    list_to_set(ListaPokemon, ListaUnica),
    lista_txt(ListaUnica, Txt),
    format('Todos los pokemones registrados son: ~w.~n', [Txt]).
%22
resp_todos_los_tipos :-
    findall(Tipo, (pokemon_de_tipo(Tipo, _)), ListaTipos),
    list_to_set(ListaTipos, ListaUnica),
    lista_txt(ListaUnica, Txt),
    format('Todos los tipos registrados son: ~w.~n', [Txt]).
