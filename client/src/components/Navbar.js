import React from 'react';

const Navbar = () => {
  return (
    <nav className="flex justify-between items-center p-6">
      <div className="text-xl font-bold"></div>
      <div className="space-x-4">
        <button className="px-4 py-2 text-gray-600 hover:text-gray-800">
          Login
        </button>
        <button className="px-4 py-2 bg-navy-900 text-white rounded-md hover:bg-navy-800">
          Sign Up
        </button>
      </div>
    </nav>
  );
};

export default Navbar;