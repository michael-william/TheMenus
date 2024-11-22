class Ideas:
    def __init__(self, Id, Title, Meal, Core, Source, Notes):
        
        # Title attributes
        self.Title = Title
        
        # Core attributes
        self.Core = Core or {}  # Placeholder for Core fields
        
        # Meal attributes
        self.Meal = Meal
        
        # Original fields for reference (can be removed if unnecessary)
        self.Id = Id
        
        # Source attributes
        self.Source = Source

        # Notes attributes
        self.Notes = Notes


        

    def __repr__(self):
        return f'<Idea {self.Title}>'
    
    def get_id(self):
        return self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'Title': self.Title,
            'Meal': self.Meal,
            'Core': self.Core,
            'Source': self.Source,
            'Notes': self.Notes
        }

    @classmethod
    def from_api_data(cls, data):
        """Class method to create an instance from API data."""
        return cls(
            Id=data.get('Id', '-'),
            Title=data.get('Title', '-'),
            Meal=data.get('Meal', '-'),
            Core=data.get('Core', '-'),
            Source=data.get('Source', '-'),
            Notes=data.get('Notes', '-')
        )