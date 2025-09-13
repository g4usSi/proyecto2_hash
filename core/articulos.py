class articulo:
    def __init__(self, titulo, autor, anio, archivo):
        self.titulo = titulo
        self.autor = autor
        self.anio = anio
        self.archivo = archivo
        self.hash = None  # se asignará al insertar en la tabla hash
        self.extension = archivo.split('.')[-1] if '.' in archivo else ''

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "anio": self.anio,
            "archivo": self.archivo,
            "hash": self.hash,
            "extension": self.extension
        }
    
    @staticmethod
    def from_dict(data):
        art = articulo(
            titulo=data.get("titulo", ""),
            autor=data.get("autor", ""),
            anio=data.get("anio", 0),
            archivo=data.get("archivo", "")
        )
        art.hash = data.get("hash")
        art.extension = data.get("extension", "")
        return art