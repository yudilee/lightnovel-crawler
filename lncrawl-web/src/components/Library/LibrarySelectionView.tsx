import { store } from '@/store';
import { Auth } from '@/store/_auth';
import type { Library, LibraryItem } from '@/types';
import { stringifyError } from '@/utils/errors';
import { BookOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Card, Input, List, message, Space, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';

interface Props {
  novelId: string;
  library?: Library;
  onCreateNew: () => void;
  onSuccess: () => void;
}

const _cache = new Map<string, Promise<LibraryItem[]>>();

function fetchAll(userId: string): Promise<LibraryItem[]> {
  if (_cache.has(userId)) {
    return _cache.get(userId)!;
  }
  const result = axios
    .get<LibraryItem[]>('/api/library/my/list')
    .then((resp) => resp.data);
  _cache.set(userId, result);
  return result;
}

export const LibrarySelectionView: React.FC<Props> = ({
  novelId,
  onCreateNew,
  onSuccess,
}) => {
  const user = Auth.select.user(store.getState());
  const [messageApi, contextHolder] = message.useMessage();

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>();
  const [libraries, setLibraries] = useState<LibraryItem[]>([]);
  const [searchValue, setSearchValue] = useState<string>('');

  useEffect(() => {
    if (user?.id) {
      setLoading(true);
      fetchAll(user.id)
        .then(setLibraries)
        .catch((err) => setError(stringifyError(err)))
        .finally(() => setLoading(false));
    } else {
      setLibraries([]);
    }
  }, [user?.id]);

  const filteredLibraries = useMemo(() => {
    if (!searchValue) {
      return libraries;
    }
    return libraries.filter((library) =>
      library.name.toLowerCase().includes(searchValue.toLowerCase())
    );
  }, [libraries, searchValue]);

  const handleLibrarySelect = async (libraryId: string) => {
    setLoading(true);
    try {
      await axios.post(`/api/library/${libraryId}/novels`, {
        novel_id: novelId,
      });
      messageApi.success('Added to library');
      onSuccess();
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Input.Search
          allowClear
          size="large"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          placeholder="Search libraries..."
        />

        {error ? (
          <Typography.Text type="danger" style={{ fontSize: 12 }}>
            Error: {error}
          </Typography.Text>
        ) : (
          <List
            size="small"
            loading={loading}
            dataSource={filteredLibraries}
            locale={{
              emptyText: 'No libraries found',
            }}
            style={{
              maxHeight: 300,
              overflowY: 'auto',
            }}
            renderItem={(library) => (
              <Card
                hoverable
                size="small"
                style={{ width: '100%', marginBottom: 2 }}
                onClick={() => handleLibrarySelect(library.id)}
              >
                <Card.Meta
                  title={library.name}
                  avatar={<BookOutlined />}
                  description={
                    library.description ? (
                      <Typography.Text type="secondary" ellipsis>
                        {library.description}
                      </Typography.Text>
                    ) : null
                  }
                />
              </Card>
            )}
          />
        )}

        <Button
          icon={<PlusOutlined />}
          onClick={onCreateNew}
          type="dashed"
          block
          size="large"
        >
          Create New Library
        </Button>
      </Space>
    </>
  );
};
