import { SearchOutlined, DownloadOutlined, GlobalOutlined, LinkOutlined } from '@ant-design/icons';
import { Button, Card, Empty, Input, List, Typography, message, Spin, Tooltip } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface SearchResult {
    title: string;
    url: string;
    info: string;
}

interface CombinedSearchResult {
    id: string;
    title: string;
    novels: SearchResult[];
}

export const OnlineSearchPage: React.FC = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<CombinedSearchResult[]>([]);
    const [searched, setSearched] = useState(false);

    const handleSearch = async (value: string) => {
        if (!value || value.length < 2) {
            message.warning('Please enter at least 2 characters');
            return;
        }

        setLoading(true);
        setSearched(true);
        setResults([]);

        try {
            const { data } = await axios.get<CombinedSearchResult[]>('/api/search/online', {
                params: {
                    query: value,
                    limit: 10,
                },
            });
            setResults(data);
        } catch (error) {
            console.error(error);
            message.error('Failed to search online sources');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async (novelUrl: string) => {
        try {
            await axios.post('/api/jobs', {
                type: 'download',
                novel_url: novelUrl,
            });
            message.success('Download job created');
            navigate('/');
        } catch (e) {
            message.error('Failed to create download job');
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: 1200, margin: '0 auto' }}>
            <Typography.Title level={2}>
                <GlobalOutlined /> Online Search
            </Typography.Title>

            <Card style={{ marginBottom: 20 }}>
                <Input.Search
                    placeholder="Search for novels (e.g., 'Barbarian Quest')"
                    enterButton={<Button type="primary" icon={<SearchOutlined />}>Search</Button>}
                    size="large"
                    onSearch={handleSearch}
                    loading={loading}
                    onChange={(e) => setQuery(e.target.value)}
                    value={query}
                />
            </Card>

            {loading && (
                <div style={{ textAlign: 'center', padding: 50 }}>
                    <Spin size="large" tip="Searching across multiple sources..." />
                </div>
            )}

            {!loading && searched && results.length === 0 && (
                <Empty description="No results found. Try a different query." />
            )}

            <List
                grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
                dataSource={results}
                renderItem={(item) => (
                    <List.Item>
                        <Card
                            title={
                                <Tooltip title={item.title}>
                                    <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                        {item.title}
                                    </div>
                                </Tooltip>
                            }
                            size="small"
                            style={{ height: '100%' }}
                        >
                            <List
                                size="small"
                                dataSource={item.novels}
                                renderItem={(novel) => (
                                    <List.Item
                                        actions={[
                                            <Tooltip title="Start Download">
                                                <Button
                                                    type="primary"
                                                    icon={<DownloadOutlined />}
                                                    size="small"
                                                    onClick={() => handleDownload(novel.url)}
                                                />
                                            </Tooltip>
                                        ]}
                                    >
                                        <List.Item.Meta
                                            title={
                                                <a href={novel.url} target="_blank" rel="noopener noreferrer">
                                                    <LinkOutlined /> {new URL(novel.url).hostname}
                                                </a>
                                            }
                                            description={
                                                novel.info ? (
                                                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                                                        {novel.info}
                                                    </Typography.Text>
                                                ) : null
                                            }
                                        />
                                    </List.Item>
                                )}
                            />
                        </Card>
                    </List.Item>
                )}
            />
        </div>
    );
};
