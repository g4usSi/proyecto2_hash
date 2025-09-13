class IndiceAutor:
    def __init__(self):
        self.indice = {}
    
    def agregar(self, art):
        clave = art.autor.strip().lower()
        if clave not in self.indice:
            self.indice[clave] = [art]
        else:
            if not any(a.hash == art.hash for a in self.indice[clave]):
                self.indice[clave].append(art)
    
    def eliminar(self, art):
        clave = art.autor.strip().lower()
        if clave in self.indice:
            self.indice[clave] = [a for a in self.indice[clave] if a.hash != art.hash]
            if not self.indice[clave]:
                del self.indice[clave]
    
    def buscar(self, autor):
        return [art for a, lista in self.indice.items() if autor.lower() in a.lower() for art in lista]
    
    def listar(self):
       return sorted(
            [art for lista in self.indice.values() for art in lista],
            key=lambda a: a.autor.lower() if a.autor else ""
        )

    
class IndiceTitulo:
    def __init__(self):
        self.indice = {}
    
    def agregar(self, art):
        clave = art.titulo.strip().lower()
        if clave not in self.indice:
            self.indice[clave] = [art]
        else:
            if not any(a.hash == art.hash for a in self.indice[clave]):
                self.indice[clave].append(art)
    
    def eliminar(self, art):
        clave = art.titulo.strip().lower()
        if clave in self.indice:
            self.indice[clave] = [a for a in self.indice[clave] if a.hash != art.hash]
            if not self.indice[clave]:
                del self.indice[clave]
    
    def buscar(self, titulo):
        return [art for t, lista in self.indice.items() if titulo.lower() in t.lower() for art in lista]
    
    def listar(self):
        return sorted(
            [art for lista in self.indice.values() for art in lista],
            key=lambda a: a.titulo.lower() if a.titulo else ""
        )
