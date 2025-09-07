// C Program to remove the odd numbers in vector using erase 
// remove idiom 
#include <algorithm> 
#include <iostream> 
#include <vector> 

// utility function to print vector 
void printV(std::vector<int>& v) 
{ 
	for (auto i : v) { 
		std::cout << i << " "; 
	} 

	std::cout << std::endl; 
} 

// driver code 
int main() 
{ 
	// declaring and defining a vector 
	std::vector<int> v{ 1, 2, 3, 4, 5, 6, 7, 8, 9 }; 

	// printing original vector 
	std::cout << "Original Vector\t\t\t: "; 
	printV(v); 

	// using remove_if method to move all the odd elements 
	// to the end and get the new logical end 
	auto new_logical_end = std::remove_if( 
		v.begin(), v.end(), [](int a) { return a % 2; }); 

	// printing vector after using remove_if() 
	std::cout << "After using remove_if()\t: "; 
	printV(v); 

	// erasing the elements from new logical end 
	v.erase(new_logical_end, v.end()); 
	std::cout << "After using erase()\t\t: "; 
	printV(v); 
}
