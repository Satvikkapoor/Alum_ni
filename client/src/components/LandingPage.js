import React, { useState } from 'react';
import { Search } from 'lucide-react';
import Navbar from './Navbar';
import SearchResults from './SearchResults';
import Footer from './Footer';


const LandingPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const categories = [
    { id: 1, name: 'Indian Internationals working in Tech' },
    { id: 2, name: 'Cathedral and John Connon Alumni' },
    { id: 3, name: 'Alumni who are a part of YC' }
  ];

  // Simulated search function - replace with actual API call
  const handleSearch = (e) => {
    e.preventDefault();
    // Simulated results - replace with actual API data
    const mockResults = [
      {
        id: 1,
        name: 'Advait Iyer',
        role: 'C++ Intern',
        company: 'Tesla',
        highSchool: 'Singapore International School',
        linkedinUrl: 'https://linkedin.com/in/sarahchen'
      },
      {
        id: 2,
        name: 'Aryan Rose',
        role: 'Hexagon',
        company: 'Mechanical Product Design',
        highSchool: 'Dubai College',
        linkedinUrl: 'https://linkedin.com/in/alexkumar'
      },
      {
        id: 3,
        name: 'Riya Kashyap',
        role: 'Tech Consultant',
        company: 'Bain',
        highSchool: 'Lagos International School',
        linkedinUrl: 'https://linkedin.com/in/mariarodriguez'
      }
    ];
    
    setSearchResults(mockResults);
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <main className="max-w-4xl mx-auto mt-32 px-4 pb-12">
        <h1 className="text-5xl font-bold text-center mb-16">
          Find your{' '}
          <span className="bg-purple-100 px-2 rounded-lg">hero.</span>
        </h1>

        <div className="relative max-w-3xl mx-auto mb-8">
          <form onSubmit={handleSearch}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Find me international students working at YC companies"
              className="w-full p-4 pr-12 text-gray-600 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent"
            />
            <button 
              type="submit"
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-navy-900 text-white p-2 rounded-md hover:bg-navy-800"
            >
              <Search size={20} />
            </button>
          </form>
        </div>

        {searchQuery === '' && (
          <div className="flex flex-wrap justify-center gap-4">
            {categories.map((category) => (
              <button
                key={category.id}
                className="px-4 py-2 bg-blue-50 text-blue-600 rounded-full hover:bg-blue-100 transition-colors"
              >
                {category.name} →
              </button>
            ))}
          </div>
        )}

        <SearchResults results={searchResults} />
      </main>
      <Footer />

    </div>
  );
};

export default LandingPage;