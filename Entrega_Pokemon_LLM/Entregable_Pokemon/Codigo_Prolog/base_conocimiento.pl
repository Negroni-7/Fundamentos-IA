%------------------ POKEMONES ---------------------------
pokemon_de_tipo(acero, [magnemite, magneton]).
pokemon_de_tipo(volador, [charizard, farfetch, gyarados,butterfree, dragonite]).
pokemon_de_tipo(agua, [squirtle, wartortle, blastoise, magikarp, gyarados, lapras, slowpoke, slowbro]).
pokemon_de_tipo(hielo, [lapras]).
pokemon_de_tipo(planta, [bulbasaur, ivysaur, venusaur]).
pokemon_de_tipo(bicho, [caterpie, metapod, butterfree]).
pokemon_de_tipo(electrico, [magnemite,magneton, electabuzz, pikachu, raichu]).
pokemon_de_tipo(normal, [farfetch, snorlax, tauros, jigglypuff, wigglytuff]).
pokemon_de_tipo(roca, [geodude, graveler, golem]).
pokemon_de_tipo(tierra, [geodude, graveler, golem]).
pokemon_de_tipo(fuego, [charmander, charmeleon, charizard]).
pokemon_de_tipo(lucha, [machop, machoke, machamp]).
pokemon_de_tipo(hada, [jigglypuff, wigglytuff]).
pokemon_de_tipo(psiquico, [mewtwo, slowpoke, slowbro]).
pokemon_de_tipo(veneno, [bulbasaur, ivysaur, venusaur, gastly, haunter, gengar]).
pokemon_de_tipo(dragon, [dratini, dragonair, dragonite]).
pokemon_de_tipo(fantasma, [gastly, haunter, gengar]).
pokemon_de_tipo(siniestro, []).

evolucion([charmander, charmeleon, charizard]).
evolucion([bulbasaur, ivysaur, venusaur]).
evolucion([squirtle, wartortle, blastoise]).
evolucion([gastly, haunter, gengar]).
evolucion([magikarp, gyarados]).
evolucion([caterpie, metapod, butterfree]).
evolucion([magnemite, magneton]).
evolucion([pikachu, raichu]).
evolucion([geodude, graveler, golem]).
evolucion([jigglypuff, wigglytuff]).
evolucion([machop, machoke, machamp]).
evolucion([dratini, dragonair, dragonite]).
evolucion([slowpoke, slowbro]).
%------------------ VENTAJAS ---------------------------
ventaja(acero, [hielo, roca, hada]).
ventaja(volador, [planta, bicho, lucha]).
ventaja(agua, [fuego, roca, tierra]).
ventaja(hielo, [volador, planta, tierra, dragon]).
ventaja(planta, [agua, tierra, roca]).
ventaja(bicho, [planta, psiquico, siniestro]).
ventaja(electrico, [volador, agua]).
ventaja(normal, []).
ventaja(roca, [hielo, volador, bicho, fuego]).
ventaja(tierra, [electrico, roca, fuego, veneno, acero]).
ventaja(fuego, [planta, acero, bicho, hielo]).
ventaja(lucha, [hielo, normal, roca, siniestro, acero]).
ventaja(hada, [lucha, dragon, siniestro]).
ventaja(psiquico, [lucha, veneno]).
ventaja(veneno, [planta, hada]).
ventaja(dragon, [dragon]).
ventaja(fantasma, [hada, fantasma]).
ventaja(siniestro, [psiquico, fantasma]).
%------------------ RESISTENTE ---------------------------
resistente(acero, [acero, volador, hielo, planta, bicho, normal, roca, hada, psiquico, dragon]).
resistente(volador, [planta, bicho, lucha]).
resistente(agua, [acero, agua, hielo, fuego]).
resistente(hielo, [hielo]).
resistente(planta, [agua, planta, electrico, tierra]).
resistente(bicho, [planta, tierra, lucha]).
resistente(electrico, [acero, volador, electrico]).
resistente(normal, []).
resistente(roca, [volador, normal, fuego, veneno]).
resistente(tierra, [roca, veneno]).
resistente(fuego, [acero, hielo, planta, bicho, fuego, hada]).
resistente(lucha, [bicho, roca, siniestro]).
resistente(hada, [bicho, lucha, siniestro]).
resistente(psiquico, [lucha, psiquico]).
resistente(veneno, [planta, bicho, lucha, hada, veneno]).
resistente(dragon, [agua, planta, electrico, fuego]).
resistente(fantasma, [bicho, veneno]).
resistente(siniestro, [fantasma, siniestro]).
%------------------ INMUNIDAD ---------------------------
inmune(acero, [veneno]).
inmune(volador, [tierra]).
inmune(normal, [fantasma]).
inmune(tierra, [electrico]).
inmune(hada, [dragon]).
inmune(fantasma, [normal,lucha]).
inmune(siniestro, [psiquico]).
%------------------ PREDICADOS ---------------------------
tipo(Pokemon, Tipo) :-                          % Consulta si un pokemon es de cierto tipo
    pokemon_de_tipo(Tipo, ListaPokemons),
    member(Pokemon, ListaPokemons).

super_efectivo(TipoAtacante, TipoDefensor) :-  % Consulta si un tipo hace efectivo a otro
    ventaja(TipoAtacante, ListaDebilidades),
    member(TipoDefensor, ListaDebilidades).

es_resistente(TipoA, TipoB):-                    % Consulta las resistencias de los tipos
    resistente(TipoA, ListaResistencias),
    member(TipoB, ListaResistencias).

es_inmune(TipoA, TipoB):-                        % Consulta las inmunidades de los tipos
    inmune(TipoA, ListaInmunidad),
    member(TipoB, ListaInmunidad).

relacion_evolutiva(PokemonA, PokemonB):-        % Consulta si dos pokemones están en la misma cadena evolutiva
    evolucion(Lista),
    member(PokemonA, Lista),
    member(PokemonB, Lista),
    PokemonA \= PokemonB.

evolucion_directa(PokemonA, PokemonB):-         % Consulta la evolución directa
    evolucion(Lista),                           % charmander -> charmeleon
    append(_, [PokemonA, PokemonB|_], Lista),
    PokemonA \= PokemonB.

es_forma_base(PokemonA):-                       % Revisa si un pokemón es su forma base
    evolucion([PokemonA|_]).

es_forma_final(PokemonA):-                      % Revisa si un pokemón es su forma final
    evolucion(Lista),
    last(Lista, PokemonA).

sin_evoluciones(PokemonA):- % Revsia si un pokemón no tiene evoluciones
    \+ (evolucion(Lista), member(PokemonA, Lista)).

tipos_de(Pokemon, Tipos) :- % Retorna los tipos del pokemón.
    setof(T, tipo(Pokemon, T), Tipos). % Se coloca cualquier letra en Tipos

doble_tipo(Pokemon) :- % Determina si un pokemón tiene 2 tipos
    tipos_de(Pokemon, [_, _]).

mismo_tipo(P1, P2) :- % Determina si dos pokemones comparten al menos un tipo
    tipo(P1, T),
    tipo(P2, T),
    P1 \= P2.

mismos_tipos(P1, P2):- % Compara si dos pokemones comparten los mismos tipos
    tipos_de(P1, [X,Y]),
    tipos_de(P2, [W,Z]),
    X == W,
    Y == Z,
    P1 \= P2.

cantidad_por_tipo(Tipo, N) :- % Retonra la cantidad de pokemones que hay de cierto tipo registrados
    pokemon_de_tipo(Tipo, Lista),
    length(Lista, N).

%Lector de lineas (para que se puedan poner espacios y no haya prroblemas, ademas de no nesesitar ocupar el punto final, creo)

leer_linea(Atom) :-
    leer_codigos(Codigos),
    atom_codes(Atom, Codigos).

leer_codigos(Codigos) :-
    get_char(C),
    (   (C == end_of_file ; C == '\n') ->
        Codigos = []
    ;   Codigos = [C|Resto],
        leer_codigos(Resto)
    ).

