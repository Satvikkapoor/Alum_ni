import React from 'react';
import SearchResultCard from './SearchResultCard';

const SearchResults = ({ results }) => {
  if (results.length === 0) {
    return null;
  }

  return (
    <div className="mt-8">
      <div className="text-gray-600 mb-4">
        Found {results.length} alumni matching your search
      </div>
      <div className="grid grid-cols-1 gap-4">
        {results.map((alumni) => (
          <SearchResultCard key={alumni.id} alumni={alumni} />
        ))}
      </div>
    </div>
  );
};

export default SearchResults;