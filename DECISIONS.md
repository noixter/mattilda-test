# Decisions
En esta seccion describo cuales fueron las decisiones tomadas para la aplicacion y por que. Soporta el proceso de pensamiento que me llevo 
al resultado final.

## domain
Separar los dominios de negocio en diferentes archivos para mejorar la organización del código.
### models
incluye todos los modelos a utilizar por el negocio, estos modelos sirven como puente entre los casos de negocio
y los elementos que se retornan de los diferentes repositorios
- Student
    - Todos los elementos mapeados de la tabla student, incluye algunos atributos adicionales como total_paid y total_debt y validaciones adicionales.
    - Se agrego un Enum para manejar los estados de los estudiantes. Sin embargo estos son manejados en la tabla SchoolStudentsTable
- Invoice
    - Todos los elementos mapeados de la tabla invoice
    - Los invoices tiene solo dos estados PENDING y PAID, estos puede ser extendidos en el futuro
- Payment
    - Todos los elementos mapeados de la tabla payment  
    - Este modelo vive en el mismo dominio que Invoice, sin embargo deberia ser un modelo independiente. No hay una implementacion tan robusta de payments
    - Fue implementado para soportar los calculos de deuda y estado de cuenta de manera mas robusta
- School
    - Todos los elementos mapeados de la tabla school
    - Total debt fue agregado como atributo adicional. Es un campo calculado que se obtiene de la suma de todos los invoices con status PENDING

### services
La logica de negocio esta contenida aca. algunos puntos importantes:
- Los calculos de deuda y estado de cuenta para estudiantes y colegios se realizan en memoria. Esto podria ser optimizado para que sea el motor de base de datos el que realice el calculo.
- El estado de cuenta podria ser calculado de manera asincrona y guardado en la base de datos para que no se calcule en cada request. (no implementado)

## infrastructure
Todos los elementos con los que interactua el dominio son agregados aqui.
- DB
    - Se implemento con SQLAlchemy como motor async. (Corresponde con los llamados async propios de fastAPI)
    - ORM con las tablas de la base de datos mapeadas. A traves del Base declarative de SQLAlchemy, crear los modelos de manera automatizada (No incluye ningun tipo de migracion) 
    
- Repositorios
    - Repositorio base (abstract) con los queries de lectura comunes para los 3 dominios principales
    - Implementacion para uso con postgres SQL (tal vez el nombre deba ser distinto)
    - La paginacion se realiza en el repositorio usando la tecnica offset y limit. Sin embargo para facilitar la implementacion de la paginacion en el servidor se implemento la libreria fastapi-pagination. Esto requirio un conversion de los params `Page y Size` a `offset y limit`.
    - Repositorios por dominio fueron creados, metodos para obtener, crear y eliminar registros (no updates por el momento).

## routers
Cada dominio tiene su propio router, esto permite que cada uno pueda escalar independientemente.
- No hay un formato especifico para los formatos de respuesta. Los elementos de tipo decimal no son UserFriendly

