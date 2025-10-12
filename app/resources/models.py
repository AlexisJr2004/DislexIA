from django.db import models

class Recurso(models.Model):
    CATEGORIA_CHOICES = [
        ('videos', 'Video'),
        ('libros', 'Libro'),
        ('enlaces', 'Enlace'),
        ('articulos', 'Artículo'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    imagen = models.ImageField(upload_to='recursos/', blank=True, null=True)
    url_externa = models.URLField(blank=True, null=True) # Para enlaces y videos
    autor = models.CharField(max_length=100, blank=True, null=True)
    duracion = models.CharField(max_length=50, blank=True, null=True)  # Ej: "15 min" o "324 pág."
    valoracion = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    visitas = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo