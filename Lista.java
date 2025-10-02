package Sistemas_programables;

/**
 *
 * @author Samuel Jafet Juárez Baliño
 * @author Ángel Javier Flores Mena
 * 
 */

public class Lista <T>{
    private Nodo inicio, fin;
    private int tamaño;
  
    //Inserta un nuevo elemento a la lista sencilla
    //@param nombre Dato a insertar.
    public void add(T nombre){
        add(new Nodo(nombre));
    }

    public void add(Nodo n){
        if(n != null){
        //revisar si la lista ya existe, sino debemos crearla
            if(inicio == null){
                inicio = fin = n;
            }
            else{ //conecta nodos en una lista existente
                fin.der = n;
                fin = fin.der;
            }
            tamaño++;
        }
    }
    
    //Método que debe regresar un nodo específico de la lista
    public T getNodo(int n) {
        if (n < 0 || n >= tamaño) {
            throw new IndexOutOfBoundsException("Índice fuera de rango: " + n);
        }
        Nodo cursor = inicio;
        for (int i = 0; i < n; i++) {
            cursor = cursor.der;
        }
        return cursor.name;
    }
  
    //Devuelve el numero de elementos contenidos en la lista sencilla
    //@return numero de elementos.
    public int size(){
        return tamaño; //devolver la cantidad de elemento de la lista
    }

    @Override
    public String toString(){
        String cadena = "Lista ("+tamaño+") { ";
        //colocar el cursor al inicio de la lista
        Nodo cursor = inicio;
        //comprobar si cursor es diferente de NULL
        while(cursor != null){
            cadena += cursor + " ";
            cursor = cursor.der;
        }
        return cadena+"}";
    }

    public String toString(int n){
        String cadena = "Lista ("+tamaño+") { ";
        //colocar el cursor al inicio de la lista
        Nodo cursor = inicio;
        //comprobar si cursor es diferente de NULL
        while(cursor != null){
            cadena += cursor + " ";
            cursor = cursor.der;
        }
        return cadena+"}";
    }

    public class Nodo {
        public T name;
        public Nodo der;

        public Nodo(T nomb){
            this.name = nomb;
        }
  
        @Override
        public String toString(){
            return name + " ";
        }
    }
}

