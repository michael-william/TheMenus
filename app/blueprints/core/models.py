class NoCoRecipes:
    def __init__(self, Id, Meal, Core, Title, LeftOvers=None, Source=None, Photo=None, Notes=None, Ingredients=None, Method=None):
        # Original fields for reference (can be removed if unnecessary)
        self.Id = Id
        
        # Meal attributes
        self.Meal = Meal

        # Title attributes
        self.Title = Title
        
        # Core attributes
        self.Core = Core or {}  # Placeholder for Core fields

        # Leftovers attributes
        self.LeftOvers = LeftOvers or {}  # Placeholder for Leftover fields
        
        # Source attributes
        self.Source = Source

        # Photo attributes
        self.Photo = Photo

        # Notes attributes
        self.Notes = Notes

        # Ingredients attributes
        self.Ingredients = Ingredients

        # Method attributes
        self.Method = Method

    def __repr__(self):
        return f'<Recipe {self.Title}>'
    
    def get_id(self):
        return self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'Meal': self.Meal,
            'Core': self.Core,
            'Title': self.Title,
            'LeftOvers': self.LeftOvers,
            'Source': self.Source,
            'Photo': self.Photo,
            'Notes': self.Notes,
            'Ingredients': self.Ingredients,
            'Method': self.Method
        }

    @classmethod
    def from_api_data(cls, data):
        """Class method to create an instance from API data."""
        return cls(
            Id=data.get('Id', 'Unknown'),
            Meal=data.get('Meal', 'Unknown'),
            Core=data.get('Core', {}),
            Title=data.get('Title', 'Untitled'),
            LeftOvers=data.get('LeftOvers', {}),
            Source=data.get('Source', 'Unknown'),
            Photo=data.get('Photo', None),
            Notes=data.get('Notes', None),
            Ingredients=data.get('Ingredients', None),
            Method=data.get('Method', None)
        )

