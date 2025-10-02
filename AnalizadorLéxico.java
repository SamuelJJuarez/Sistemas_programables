package Sistemas_programables;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

/**
 *
 * @author Samuel Jafet Juárez Baliño
 * @author Ángel Javier Flores Mena
 */

public class AnalizadorLéxico {
    private String nombreArchivo = "src/léxicosintáctico/prueba.txt"; //Nombre del archivo
    private String[] palabrasReservadas = {"programa", "binario", "octal", "hexad", "leer", "escribir", "finprograma"};
    //Arreglo de palabras reservadas
    private int[] atriReservada = {300, 301, 302, 303, 304, 305, 306}; //Arreglo con los atributos de las palabras reservadas
    private String[] caracteresSimples = {";", "=", "+", "-", "/", "*", ",", "(", ")"}; //Arreglo con los caracteres simples
    private int[] atriCarSimp = {59, 61, 43, 45, 47, 42, 44, 40, 41}; //Arreglo con los atributos de los caracteres simples
    private int numLinea = 0; //Variable que cuenta la línea que se está analizando
    private String [] clasificaciones = {"id", "litbinaria", "litoctal", "lithexa"};
    private int[] atributos = {400, 401, 402, 403}; //Arreglo con los atributos de las clasificaciones
    private Lista<String[]> listaDeSimbolos = new Lista<>(); //Lista con los símbolos y su atributo
    Lista<String[]> listaDeTokens = new Lista<>(); //Lista de tokens válidos
    private int f = 0; //Variable para ir recorriendo el archivo
    private String contenido = ""; //Varibale con todo el contenido del archivo
    private String[] arregloPos; //Arreglo con todos los elementos posibles
    private int[] atributosComp; //Arreglo con todos los atributos
    private int idAtri = 500;
    private int tipoVar = 0;
    private String[] tipos = {"Binario", "Octal", "Hexadecimal"};
    private String posibleValor = "";
    private boolean asignandoValor = false;
    private String pendienteAsigna = "";
    
    //Constructor que llama a leer el archivo 
    public AnalizadorLéxico(){
        leerArchivo();
    }
    
    //Método que lee el archivo
    private void leerArchivo() {
        try {
            File archivo = new File(nombreArchivo);
            Scanner lector = new Scanner(archivo);
            //Mientras pueda leer
            while (lector.hasNextLine()) {
                //Lee la línea
                String linea = lector.nextLine();
                //Agrega la línea al contenido del archivo y agrega un salto de línea
                contenido += linea + "\n";
            }
            lector.close();
            System.out.println("\u001B[32mPROGRAMA A ANALIZAR:\n\u001B[0m");
            System.out.println(contenido);
            
            //Junta los arreglos de atributos y clasificaciones léxicas
            juntarArreglos();
        } catch (FileNotFoundException e) {
            System.out.println("Ocurrió un error al leer el archivo.");
        }
    }
    
    //Método para llamar la obtención de un token
    public int obtenerLexico(){
        return automata(contenido);
    }

    //Método que clasifica la palabra leída
    private int automata(String linea) {
        String lexema = ""; 
        int estado = 0; //Variable que indica en que estado del autómata estamos
        //Mientras no lleguemos al final de la línea
        while (f < linea.length()) {
            char c = linea.charAt(f); //Caracter que se está leyendo
            char cAux = 0; //Caracter siguiente al que se está leyendo
            if(f < linea.length()-1){
                cAux = linea.charAt(f+1);
            }

            switch (estado) {
                //Caso que asigna la clasificación inicial
                case 0:
                    lexema = "";
                    if (c >= '0' && c <= '9') { //Si es un número entre 0 y 9
                        if (c == '0' || c == '1') { //Si es un cero o uno
                            estado = 1; // Puede ser Binario, Octal, Decimal o Hexadecimal
                        } else if (c >= '2' && c <= '7') { //Si es un valor entre 2 y 7
                            estado = 2; // Puede ser Octal, Decimal o Hexadecimal
                        } else {
                            estado = 3; // Puede ser Decimal o Hexadecimal
                        }
                    } else if (c >= 'A' && c <= 'F') { //Si es una letra entre A y F
                        estado = 4; // Puede ser Hexadecimal
                    } else if (esSimbolo(c)) { //Si es un caracter
                        estado = 5; 
                    } else if ((c >= 'a' && c <= 'z') || c == 'ñ') { //Si es una letra minúscula
                        estado = 6;
                    } else if (c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f'){ //Si es un espacio en blanco
                        if(c == '\n'){
                            numLinea++;
                        }
                        f++;
                    } else {
                        estado = 7;
                    }
                    break;

                // Puede ser Binario, Octal, Decimal o Hexadecimal    
                case 1:
                    if (c == '0' || c == '1') { //Si es 1 o 0
                        if(f == linea.length()-1){
                            lexema += c;
                            f++;
                            return guardarToken(lexema, 3); // Decimal
                        } else {
                            lexema += c;
                            f++; 
                        }
                    } else if (c == 'B') { //Si tiena la B
                        //Si tiene algo de otra clasificación numérica después de la B
                        if ((cAux >= '0' && cAux <= '9') || (cAux >= 'A' && cAux <= 'F')) {
                            estado = 4; //Puede ser Hexadecimal
                        } else { //Si lo que sigue no es de otra clasificación numérica
                            lexema += c;
                            f++;
                            return guardarToken(lexema, 1); // Binario
                        }
                    } else if (c >= '2' && c <= '7') { //Comprueba si es un número entre 2 y 7
                        lexema += c;
                        estado = 2; // Puede ser Octal, Decimal o Hexadecimal
                        f++;
                    } else if (c >= '8' && c <= '9') { //Comprueba si es un número entre 8 y 9
                        lexema += c;
                        estado = 3; //Puede ser Decimal o Hexadecimal
                        f++;
                    } else if (c >= 'A' && c <= 'F') { //Si es una letra entre A y F
                        lexema += c;
                        estado = 4; //Puede ser Hexadecimal
                        f++;
                    } else if (c == 'X') {  //Si tiene la X
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 4); // Hexadecimal
                    } else if (c == 'O') { //Si tiene la O
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 2); // Octal
                    } else if ((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)) { //Si hay un espacio en blanco o caracter simple
                        if(c == '\n'){
                            numLinea++;
                        }
                        return guardarToken(lexema, 3); // Decimal
                        // no avanzar f, para procesar símbolo o espacio
                    } else { //Va al estado de error
                        estado = 7;
                    }
                    break;

                //Puede ser Octal, Decimal o Hexadecimal 
                case 2:
                    if (c >= '0' && c <= '7') { //Comprueba si es un número entre 2 y 7
                        if(f == linea.length()-1){
                            lexema += c;
                            f++;
                            return guardarToken(lexema, 3); // Decimal
                        } else {
                            lexema += c;
                            f++; 
                        }
                    } else if (c == 'O') { //Si tiene la O
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 2); // Octal
                    } else if (c >= '8' && c <= '9') {  //Comprueba si es un número entre 8 y 9
                        lexema += c;
                        estado = 3; //Puede ser Decimal o Hexadecimal 
                        f++;
                    } else if (c >= 'A' && c <= 'F') { //Si es una letra entre A y F
                        lexema += c;
                        estado = 4; //Puede ser Hexadecimal
                        f++;
                    } else if (c == 'X') {  //Si tiene la X
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 4); // Hexadecimal
                    } else if ((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)) { //Si hay un espacio en blanco o caracter simple
                        if(c == '\n'){
                            numLinea++;
                        }
                        return guardarToken(lexema, 3); // Decimal
                        // no avanzar f, para procesar símbolo o espacio
                    } else { //Va al estado de error
                        estado = 7;
                    }
                    break;

                //Puede ser Decimal o Hexadecimal
                case 3:
                    if (c >= '0' && c <= '9') {
                        if(f == linea.length()-1){
                            lexema += c;
                            f++;
                            return guardarToken(lexema, 3); // Decimal
                        } else {
                            lexema += c;
                            f++; 
                        }
                    } else if ((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)) { //Si hay un espacio en blanco o caracter simple
                        if(c == '\n'){
                            numLinea++;
                        }
                        return guardarToken(lexema, 3); // Decimal
                        // no avanzar f, para procesar símbolo o espacio
                    } else if (c >= 'A' && c <= 'F') { //Si es una letra entre A y F
                        lexema += c;
                        estado = 4; //Puede ser Hexadecimal
                        f++;
                    } else if (c == 'X') {  //Si tiene la X
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 4); // Hexadecimal
                    } else { //Va al estado de error
                        estado = 7;
                    }
                    break;

                //Puede ser Hexadecimal    
                case 4:
                    if ((c >= 'A' && c <= 'F') || (c >= '0' && c <= '9')) { //Si es una letra entre A y F o un número
                        if(f == linea.length()-1){
                            lexema += c;
                            f++;
                            return guardarToken(lexema, 3); // Decimal
                        } else {
                            lexema += c;
                            f++; 
                        }
                    } else if (c == 'X') { //Si tiene la X
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 4); // Hexadecimal
                    } else if ((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)) { //Si hay un espacio en blanco o caracter simple
                        if(c == '\n'){
                            numLinea++;
                        }
                        return guardarToken(lexema, 3); // Decimal
                        // no avanzar f, para procesar símbolo o espacio
                    } else { //Va al estado de error
                        estado = 7;
                    }
                    break;

                //Es caracter especial 
                case 5:
                    if (esSimbolo(c)) {
                        lexema += c;
                        f++;
                        return guardarToken(lexema, 5); // Caracter especial
                    }
                    break;

                //Es letra en minúscula
                case 6:
                    //Si es una letra y no es el final de la línea
                    if (((c >= 'a' && c <= 'z') || c == 'ñ') && f < linea.length()-1) {
                        lexema += c;
                        f++;
                    } else if (f == linea.length()-1){ //Si es el final de la línea
                        if ((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)) {
                            if(c == '\n'){
                                numLinea++;
                            }
                            return guardarToken(lexema, 6); // Identificador
                        } else {
                            lexema += c;
                            f++;
                            return guardarToken(lexema, 6); // Identificador
                        }
                    } else if ((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)) { //Si hay un espacio en blanco o caracter simple
                        if(c == '\n'){
                            numLinea++;
                        }
                        return guardarToken(lexema, 6); // Identificador
                        // no avanzar f, lo vuelve a procesar
                    } else { //Va al estado de error
                        estado = 7;
                    }
                    break;

                //Estado de error    
                case 7:
                    //Cuando haya un espacio en blanco o caracter simple
                    if((c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f') || esSimbolo(c)){
                        if(c == '\n'){
                            numLinea++;
                        }
                        return guardarToken(lexema, 0); // Error
                        // no avanzar f, lo vuelve a procesar
                    } else { //Mientras no haya un espacio en balnco o caracter simple
                        lexema += c;
                        f++;
                    }
                    break;
            }
        }
        
        return -1; //Regresa un -1 que es el valor del fin de archivo
    }

    //Método para comprobar si es un caracter especial
    private boolean esSimbolo(char c) {
        //Recorrerá todos los caracteres simples
        for (String s : caracteresSimples) {
            //Compara si es igual al caracter
            if (s.equals(String.valueOf(c))) {
                //Si es igual a alguno regresa true
                return true;
            }
        }
        //Si no es igual a ninguno regresa falso
        return false;
    }

    //Método que regresará el token de la palabra leída
    private int guardarToken(String lexema, int tipo) {
        switch (tipo) {
            case 0: //Si es un error
                return -1; //Se regresa un -1 para indicar que no se generó un token
            case 1: //Si es un número binario
                listaDeTokens.add(new String[]{"Binario", atributos[1]+"", lexema, numLinea+""}); //Se agrega a la tabla de tokens
                if(asignandoValor = true){
                    posibleValor += lexema;
                }
                modificarTabSimCons(lexema, "Binario");
                return atributos[1]; //Se regresa el token de los binarios
            case 2: //Si es un octal
                listaDeTokens.add(new String[]{"Octal", atributos[2]+"", lexema, numLinea+""}); //Se agrega a la tabla de tokens
                if(asignandoValor = true){
                    posibleValor += lexema;
                }
                modificarTabSimCons(lexema, "Octal");
                return atributos[2]; //Se regresa el token de los octales
            case 3: //Si es un error
                return -1; //Se regresa un -1 para indicar que no se generó un token
            case 4: //Si es un hexadecimal
                listaDeTokens.add(new String[]{"Hexadecimal", atributos[3]+"", lexema, numLinea+""}); //Se agrega a la tabla de tokens
                if(asignandoValor = true){
                    posibleValor += lexema;
                }
                modificarTabSimCons(lexema, "Hexadecimal");
                return atributos[3]; //Se regresa el token de los hexadecimales
            case 5: //Si es un caracter simple
                //Ciclo para asignar su atributo
                for (int i = 0; i < caracteresSimples.length; i++) {
                    if(lexema.equals(caracteresSimples[i])){
                        if(lexema.equals("=")){
                            //Se agrega a la tabla de tokens
                            listaDeTokens.add(new String[]{"Asignacion", atriCarSimp[i]+"", lexema, numLinea+""});
                            asignandoValor = true;
                        } else if(lexema.equals("+")) {
                            listaDeTokens.add(new String[]{"Suma", atriCarSimp[i]+"", lexema, numLinea+""});
                        } else if(lexema.equals("-")) {
                            listaDeTokens.add(new String[]{"Resta", atriCarSimp[i]+"", lexema, numLinea+""});
                        } else if(lexema.equals("/")) {
                            listaDeTokens.add(new String[]{"Division", atriCarSimp[i]+"", lexema, numLinea+""});
                        } else if(lexema.equals("*")) {
                            listaDeTokens.add(new String[]{"Multiplicacion", atriCarSimp[i]+"", lexema, numLinea+""});
                        } else {
                            listaDeTokens.add(new String[]{"Caracter simple", atriCarSimp[i]+"", lexema, numLinea+""});
                        }
                        
                        if(lexema.equals(";")){
                            tipoVar = 0;
                            asignandoValor = false;
                            posibleValor = "";
                        }
                        
                        return atriCarSimp[i]; //Se regresa el token de ese caracter simple
                    }
                }
            case 6: //Si es un identificador o palabra reservada
                boolean esReservada = false;
                //Ciclo para verificar si el lexema es una palabra reservada
                for (int i = 0; i < palabrasReservadas.length; i++) {
                    //Si es una reservada
                    if (lexema.equals(palabrasReservadas[i])) {
                        //Se agrega a la tabla de tokens y se le asigna su atributo
                        esReservada = true;
                        if(numLinea == 0){
                            listaDeTokens.add(new String[]{"Palabra reservada", atriReservada[i]+"", lexema, "1"});
                        } else if (i == palabrasReservadas.length-1){
                            listaDeTokens.add(new String[]{"Palabra reservada", atriReservada[i]+"", lexema, numLinea-1+""});
                        } else {
                            listaDeTokens.add(new String[]{"Palabra reservada", atriReservada[i]+"", lexema, numLinea+""});
                        }
                        
                        if(lexema.equals("binario")){
                            tipoVar = 1;
                        } else if(lexema.equals("octal")){
                            tipoVar = 2;
                        } else if(lexema.equals("hexad")){
                            tipoVar = 3;
                        }
                        
                        return atriReservada[i]; //Se regresa el token de esa palabra reservada
                    }
                }
                if (!esReservada) { //Si es un atributo
                    listaDeTokens.add(new String[]{"Identificador", atributos[0]+"", lexema, numLinea+""});
                    if(asignandoValor = true){
                        posibleValor += lexema;
                    } else {
                        pendienteAsigna = lexema;
                    }
                    modificarTabSimIden(lexema);
                    return atributos[0]; //Se regresa el token de los identificadores
                }
                break;
        }
        
        return -1;
    }
    
    private void modificarTabSimIden(String lexema){
        if(listaDeSimbolos.size() == 0){
            //Si es el primer identificador se agrega a la tabla de símbolos con su id de token
            if(listaDeTokens.size() > 1){
                if (tipoVar != 0){
                    listaDeSimbolos.add(new String[]{lexema, tipos[tipoVar-1], idAtri+"", "1", numLinea+"", ""});
                    idAtri++;
                } else {
                    listaDeSimbolos.add(new String[]{lexema, "", idAtri+"", "1", numLinea+"", ""});
                    idAtri++;
                }
            }
        } else { //Si ya hay algun identificador en la tabla de símbolos
            boolean registrada = false;
            //Ciclo para recorrer la tabla
            for (int i = 0; i < listaDeSimbolos.size(); i++) {
                //Si el identificador actual ya se encuentra en la tabla
                if(lexema.equals(listaDeSimbolos.getNodo(i)[0])){
                    registrada = true;
                    break;
                }
            }
            //Si el identificador aún no se encontraba en la tabla
            if(!registrada){
                //Se agrega a la tabla de símbolos con su id de token
                if (tipoVar != 0){
                    listaDeSimbolos.add(new String[]{lexema, tipos[tipoVar-1], idAtri+"", "1", numLinea+"", ""});
                    idAtri++;
                } else {
                    listaDeSimbolos.add(new String[]{lexema, "", idAtri+"", "1", numLinea+"", ""});
                    idAtri++;
                }
            } else {
                for (int i = 0; i < listaDeSimbolos.size(); i++) {
                    //Si el identificador actual ya se encuentra en la tabla
                    if(lexema.equals(listaDeSimbolos.getNodo(i)[0])){
                        int rep = Integer.parseInt(listaDeSimbolos.getNodo(i)[3]) + 1;
                        listaDeSimbolos.getNodo(i)[3] = rep+"";
                        String num = listaDeSimbolos.getNodo(i)[4] + ", " + numLinea;
                        listaDeSimbolos.getNodo(i)[4] = num;
                        
                        if(tipoVar != 0){
                            if(listaDeSimbolos.getNodo(i)[1].equals("")){
                                listaDeSimbolos.getNodo(i)[1] = tipos[tipoVar-1];
                            } else {
                                System.out.println("ERROR: No se puede alterar el tipo de un identificador");
                            }
                        }
                        
                        if(asignandoValor == true && pendienteAsigna.equals(listaDeSimbolos.getNodo(i)[0])){
                            if(listaDeSimbolos.getNodo(i)[5].equals("")){
                                listaDeSimbolos.getNodo(i)[5] = posibleValor;
                            } else {
                                System.out.println("ERROR: No se puede alterar el valor de un identificador");
                            }
                        }
                    }
                }
            }
        }
    }
    
    
    private void modificarTabSimCons(String lexema, String tipo){
        if(listaDeSimbolos.size() == 0){
            //Si es ek primer símbolo se agrega a la tabla de símbolos con su id de token
            listaDeSimbolos.add(new String[]{lexema, tipo, "", "1", numLinea+"", lexema});
            idAtri++;
        } else { //Si ya hay algun identificador en la tabla de símbolos
            boolean registrada = false;
            //Ciclo para recorrer la tabla
            for (int i = 0; i < listaDeSimbolos.size(); i++) {
                //Si el identificador actual ya se encuentra en la tabla
                if(lexema.equals(listaDeSimbolos.getNodo(i)[0])){
                    registrada = true;
                    break;
                }
            }
            //Si el identificador aún no se encontraba en la tabla
            if(!registrada){
                //Se agrega a la tabla de símbolos con su id de token
                listaDeSimbolos.add(new String[]{lexema, tipo, "", "1", numLinea+"", lexema});
                idAtri++;
            } else {
                for (int i = 0; i < listaDeSimbolos.size(); i++) {
                    //Si el identificador actual ya se encuentra en la tabla
                    if(lexema.equals(listaDeSimbolos.getNodo(i)[0])){
                        int rep = Integer.parseInt(listaDeSimbolos.getNodo(i)[3]) + 1;
                        listaDeSimbolos.getNodo(i)[3] = rep+"";
                        String num = listaDeSimbolos.getNodo(i)[4] + ", " + numLinea;
                        listaDeSimbolos.getNodo(i)[4] = num;
                    }
                }
            }
        }
    }
    
    //Método para imprimir la tabla de símbolos
    public void imprimirTabSimbolos() {
        int anchoCol1 = 30; //Identificador
        int anchoCol2 = 20; //Tipo
        int anchoCol3 = 15; //Codigo de Token
        int anchoCol4 = 20; //Repeticiones
        int anchoCol5 = 30; //Numero de linea
        int anchoCol6 = 20; //Valor
        
        //Título de la tabla
        System.out.printf("%-" + anchoCol1 + "s%-" + anchoCol2 + "s%-" + anchoCol3 + "s%-" + anchoCol4 + "s%-" + anchoCol5 + "s%-" + anchoCol6 +
                "s\n", "Token", "Tipo", "Id_Token", "Repeticiones", "Linea", "Valor");
        System.out.println("-".repeat(anchoCol1 + anchoCol2 + anchoCol3 + anchoCol4 + anchoCol5 + anchoCol6));

        //Impresión de la tabla
        for (int i = 0; i < listaDeSimbolos.size(); i++) {
            String identificador = listaDeSimbolos.getNodo(i)[0];
            String tipo = listaDeSimbolos.getNodo(i)[1];
            String codigo = listaDeSimbolos.getNodo(i)[2];
            String repeticiones = listaDeSimbolos.getNodo(i)[3];
            String num = listaDeSimbolos.getNodo(i)[4];
            String valor = listaDeSimbolos.getNodo(i)[5];
            System.out.printf("%-" + anchoCol1 + "s%-" + anchoCol2 + "s%-" + anchoCol3 + "s%-" + anchoCol4 + "s%-" + anchoCol5 + "s%-" + anchoCol6 +
                    "s\n", identificador, tipo, codigo, repeticiones, num, valor);
        }
    }
    
    //Método para imprimir la tabla de palabras reservadas
    public void imprimirTabReservadas() {
        int anchoCol1 = 30; //Palabras reservadas
        int anchoCol2 = 15; //Atributo

        //Título de la tabla
        System.out.printf("%-" + anchoCol1 + "s%-" + anchoCol2 + "s\n", "Palabras reservadas", "Atributo");
        System.out.println("-".repeat(anchoCol1 + anchoCol2));

        //Impresión de la tabla
        for (int i = 0; i < palabrasReservadas.length; i++) {
            String palabra = palabrasReservadas[i];
            String atributo = atriReservada[i]+"";
            System.out.printf("%-" + anchoCol1 + "s%-" + anchoCol2 + "s\n", palabra, atributo);
        }
    }
    
    //Método para imprimir la tabla de tokens
    public void imprimirTabTokens() {
        int anchoCol1 = 25; // Clasificación léxica
        int anchoCol2 = 15; // Atributo
        int anchoCol3 = 25; // Lexema
        int anchoCol4 = 15; // Número de línea

        //Título de la tabla
        System.out.printf("%-" + anchoCol1 + "s%-" + anchoCol2 + "s%-" + anchoCol3 + "s%-" + anchoCol4 + "s\n", 
                          "Clasificacion lexica", "Atributo", "Lexema", "Num. Linea");
        System.out.println("-".repeat(anchoCol1 + anchoCol2 + anchoCol3+ anchoCol4));

        //Impresión de la tabla
        for (int i = 0; i < listaDeTokens.size(); i++) {
            String clasificacion = listaDeTokens.getNodo(i)[0];
            String atributo = listaDeTokens.getNodo(i)[1];
            String lexema = listaDeTokens.getNodo(i)[2];
            String numlin = listaDeTokens.getNodo(i)[3];
            System.out.printf("%-" + anchoCol1 + "s%-" + anchoCol2 + "s%-" + anchoCol3 + "s%-" + anchoCol4 + "s\n",
                              clasificacion, atributo, lexema, numlin);
        }
    }

    //Junta los arreglos de clasificaciones y atributos
    private void juntarArreglos() {
        int tamaño = palabrasReservadas.length + caracteresSimples.length + clasificaciones.length;
        arregloPos = new String[tamaño];
        atributosComp = new int[tamaño];
        int posicion = 0;
        for (int i = 0; i < palabrasReservadas.length; i++) {
            arregloPos[posicion] = palabrasReservadas[i];
            atributosComp[posicion] = atriReservada[i];
            posicion++;
        } 
        for (int i = 0; i < caracteresSimples.length; i++) {
            arregloPos[posicion] = caracteresSimples[i];
            atributosComp[posicion] = atriCarSimp[i];
            posicion++;
        }
        for (int i = 0; i < clasificaciones.length; i++) {
            arregloPos[posicion] = clasificaciones[i];
            atributosComp[posicion] = atributos[i];
            posicion++;
        }
    }

    //Obtiene el arreglo de las clasificaciones
    public String[] getArregloPos() {
        return arregloPos;
    }

    //Obtiene el arreglo de los atributos
    public int[] getAtributosComp() {
        return atributosComp;
    }

    //Obtiene el número de línea que se está analizando
    public int getNumLinea() {
        return numLinea;
    }
}
