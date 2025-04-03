import { useState } from 'react';
import {
  Box,
  Input,
  SimpleGrid,
  Spinner,
  Center,
  Image,
  VStack,
} from '@chakra-ui/react';
import axios from 'axios';

interface GifPanelProps {
  gifs?: string[];
  isLoading?: boolean;
  mode?: 'display' | 'search';
  onGifSelect: (gifUrl: string) => void;
}

export const GifPanel = ({ gifs = [], isLoading = false, mode = 'display', onGifSelect }: GifPanelProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounce function
  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  };

  // Search for GIFs
  const searchGifs = async (query: string) => {
    if (!query) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.post('http://localhost:5001/search_gifs', {
        query: query
      });
      
      if (response.data.gifs) {
        setSearchResults(response.data.gifs);
      }
    } catch (error) {
      console.error('Error searching GIFs:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Debounced search function
  const debouncedSearch = debounce(searchGifs, 500);

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    debouncedSearch(query);
  };

  const displayGifs = mode === 'search' ? searchResults : gifs;
  const loading = mode === 'search' ? isSearching : isLoading;

  return (
    <Box>
      {mode === 'search' && (
        <Input
          placeholder="Search GIFs..."
          value={searchQuery}
          onChange={handleSearchChange}
          mb={4}
        />
      )}

      {loading ? (
        <Center h="200px">
          <Spinner size="xl" />
        </Center>
      ) : displayGifs.length === 0 ? (
        <Center h="200px">
          <VStack>
            {mode === 'search' ? (
              searchQuery ? 
                <Box>No GIFs found for "{searchQuery}"</Box> :
                <Box>Type to search for GIFs</Box>
            ) : (
              <Box>No GIFs available</Box>
            )}
          </VStack>
        </Center>
      ) : (
        <SimpleGrid columns={3} spacing={2} maxH="300px" overflowY="auto">
          {displayGifs.map((gifUrl, index) => (
            <Box
              key={index}
              cursor="pointer"
              onClick={() => onGifSelect(gifUrl)}
              borderRadius="md"
              overflow="hidden"
              _hover={{ opacity: 0.8 }}
            >
              <Image
                src={gifUrl}
                alt={`GIF ${index + 1}`}
                objectFit="cover"
                w="100%"
                h="100px"
              />
            </Box>
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
}; 