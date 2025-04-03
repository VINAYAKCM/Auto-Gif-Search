import { useState, useCallback } from 'react';
import {
  Box,
  SimpleGrid,
  Image,
  Spinner,
  Center,
  Text,
  Input,
  InputGroup,
  InputRightElement,
  IconButton,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Flex,
} from '@chakra-ui/react';
import { FaSearch, FaTimes } from 'react-icons/fa';
import axios from 'axios';

interface GifPanelProps {
  gifs: string[];
  isLoading: boolean;
  onGifSelect: (gifUrl: string) => void;
}

export const GifPanel = ({ gifs, isLoading, onGifSelect }: GifPanelProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [trendingGifs, setTrendingGifs] = useState<string[]>([]);
  const [isTrendingLoading, setIsTrendingLoading] = useState(false);

  // Fetch trending GIFs
  const fetchTrendingGifs = useCallback(async () => {
    if (trendingGifs.length > 0) return; // Don't fetch if we already have trending GIFs
    setIsTrendingLoading(true);
    try {
      const response = await axios.get('http://localhost:5001/trending_gifs');
      setTrendingGifs(response.data.gifs || []);
    } catch (error) {
      console.error('Error fetching trending GIFs:', error);
    } finally {
      setIsTrendingLoading(false);
    }
  }, [trendingGifs]);

  // Manual search function
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const response = await axios.post('http://localhost:5001/search_gifs', {
        query: searchQuery
      });
      setSearchResults(response.data.gifs || []);
    } catch (error) {
      console.error('Error searching GIFs:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery]);

  // Clear search
  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
  };

  return (
    <Box
      maxH="400px"
      overflowY="auto"
      borderWidth="1px"
      borderRadius="lg"
      p={2}
      bg="white"
      position="relative"
    >
      <Tabs variant="soft-rounded" colorScheme="blue" size="sm" mb={2}>
        <TabList>
          <Tab>Suggestions</Tab>
          <Tab onClick={fetchTrendingGifs}>Trending</Tab>
          <Tab>Search</Tab>
        </TabList>

        <TabPanels>
          {/* Suggested GIFs Panel */}
          <TabPanel p={1}>
            {isLoading ? (
              <Center py={8}>
                <Spinner size="lg" color="blue.500" />
              </Center>
            ) : gifs.length === 0 ? (
              <Center py={8}>
                <Text color="gray.500">No suggestions yet. Try typing a message!</Text>
              </Center>
            ) : (
              <SimpleGrid columns={3} spacing={2}>
                {gifs.map((gifUrl, index) => (
                  <Box
                    key={index}
                    cursor="pointer"
                    onClick={() => onGifSelect(gifUrl)}
                    _hover={{ opacity: 0.8 }}
                    transition="opacity 0.2s"
                  >
                    <Image
                      src={gifUrl}
                      alt={`GIF ${index + 1}`}
                      borderRadius="md"
                      objectFit="cover"
                      w="full"
                      h="100px"
                      loading="lazy"
                      fallback={<Spinner size="sm" />}
                    />
                  </Box>
                ))}
              </SimpleGrid>
            )}
          </TabPanel>

          {/* Trending GIFs Panel */}
          <TabPanel p={1}>
            {isTrendingLoading ? (
              <Center py={8}>
                <Spinner size="lg" color="blue.500" />
              </Center>
            ) : trendingGifs.length === 0 ? (
              <Center py={8}>
                <Text color="gray.500">No trending GIFs available</Text>
              </Center>
            ) : (
              <SimpleGrid columns={3} spacing={2}>
                {trendingGifs.map((gifUrl, index) => (
                  <Box
                    key={index}
                    cursor="pointer"
                    onClick={() => onGifSelect(gifUrl)}
                    _hover={{ opacity: 0.8 }}
                    transition="opacity 0.2s"
                  >
                    <Image
                      src={gifUrl}
                      alt={`Trending GIF ${index + 1}`}
                      borderRadius="md"
                      objectFit="cover"
                      w="full"
                      h="100px"
                      loading="lazy"
                      fallback={<Spinner size="sm" />}
                    />
                  </Box>
                ))}
              </SimpleGrid>
            )}
          </TabPanel>

          {/* Search Panel */}
          <TabPanel p={1}>
            <Flex direction="column" gap={2}>
              <InputGroup size="sm">
                <Input
                  placeholder="Search GIFs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  pr="4.5rem"
                />
                <InputRightElement width="4.5rem">
                  {searchQuery && (
                    <IconButton
                      h="1.75rem"
                      size="sm"
                      aria-label="Clear search"
                      icon={<FaTimes />}
                      onClick={clearSearch}
                    />
                  )}
                  <IconButton
                    h="1.75rem"
                    size="sm"
                    aria-label="Search"
                    icon={<FaSearch />}
                    onClick={handleSearch}
                    ml={1}
                  />
                </InputRightElement>
              </InputGroup>

              {isSearching ? (
                <Center py={8}>
                  <Spinner size="lg" color="blue.500" />
                </Center>
              ) : searchResults.length > 0 ? (
                <SimpleGrid columns={3} spacing={2}>
                  {searchResults.map((gifUrl, index) => (
                    <Box
                      key={index}
                      cursor="pointer"
                      onClick={() => onGifSelect(gifUrl)}
                      _hover={{ opacity: 0.8 }}
                      transition="opacity 0.2s"
                    >
                      <Image
                        src={gifUrl}
                        alt={`Search Result ${index + 1}`}
                        borderRadius="md"
                        objectFit="cover"
                        w="full"
                        h="100px"
                        loading="lazy"
                        fallback={<Spinner size="sm" />}
                      />
                    </Box>
                  ))}
                </SimpleGrid>
              ) : searchQuery ? (
                <Center py={8}>
                  <Text color="gray.500">No results found</Text>
                </Center>
              ) : (
                <Center py={8}>
                  <Text color="gray.500">Type something to search</Text>
                </Center>
              )}
            </Flex>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}; 