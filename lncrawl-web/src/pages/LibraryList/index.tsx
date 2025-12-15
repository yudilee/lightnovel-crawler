import { Auth } from '@/store/_auth';
import type { LibrarySummary, Paginated } from '@/types';
import { stringifyError } from '@/utils/errors';
import { LockOutlined } from '@ant-design/icons';
import { Divider, Space, message } from 'antd';
import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { CreateLibraryModal } from './components/CreateLibraryModal';
import { LibraryListHeader } from './components/LibraryListHeader';
import { LibrarySection } from './components/LibrarySection';

export const LibraryListPage: React.FC = () => {
  const navigate = useNavigate();
  const user = useSelector(Auth.select.user);
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [messageApi, contextHolder] = message.useMessage();

  const [loading, setLoading] = useState(true);
  const [myLibraries, setMyLibraries] = useState<Paginated<LibrarySummary>>();
  const [allLibraries, setAllLibraries] = useState<Paginated<LibrarySummary>>();
  const [publicLibraries, setPublicLibraries] =
    useState<Paginated<LibrarySummary>>();

  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const loadLibraries = useCallback(
    async (myPage = 1, publicPage = 1, limit = 12) => {
      setLoading(true);
      try {
        if (isAdmin) {
          const offsetAll = (publicPage - 1) * limit;
          const all = await axios.get<Paginated<LibrarySummary>>(
            '/api/library/all',
            {
              params: { offset: offsetAll, limit },
            }
          );
          setAllLibraries(all.data);
          setMyLibraries(undefined);
          setPublicLibraries(undefined);
        } else {
          const offsetMy = (myPage - 1) * limit;
          const offsetPub = (publicPage - 1) * limit;
          const [mine, shared] = await Promise.all([
            axios.get<Paginated<LibrarySummary>>('/api/library/my', {
              params: { offset: offsetMy, limit },
            }),
            axios.get<Paginated<LibrarySummary>>('/api/library/public', {
              params: { offset: offsetPub, limit },
            }),
          ]);
          setMyLibraries(mine.data);
          setPublicLibraries(shared.data);
        }
      } catch (err) {
        messageApi.error(stringifyError(err));
      } finally {
        setLoading(false);
      }
    },
    [isAdmin, messageApi]
  );

  useEffect(() => {
    loadLibraries();
  }, [loadLibraries]);

  const handleCreate = async (values: {
    name: string;
    description?: string;
    is_public?: boolean;
  }) => {
    setCreating(true);
    try {
      await axios.post('/api/library', {
        name: values.name,
        description: values.description,
        is_public: Boolean(values.is_public),
      });
      messageApi.success('Library created');
      setCreateOpen(false);
      loadLibraries();
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setCreating(false);
    }
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {contextHolder}
      <LibraryListHeader onCreateClick={() => setCreateOpen(true)} />

      {!isAdmin && (
        <section>
          <Divider style={{ margin: '12px 0' }} />
          <LibrarySection
            title="My Libraries"
            icon={<LockOutlined />}
            libraries={myLibraries}
            userId={user!.id}
            loading={loading}
            emptyText="You have no libraries yet."
            onPageChange={(page) => loadLibraries(page, undefined)}
            onSelect={(id) => navigate(`/library/${id}`)}
          />
        </section>
      )}

      <section>
        <Divider style={{ margin: '12px 0' }} />
        <LibrarySection
          title={isAdmin ? 'All Libraries' : 'Public Libraries'}
          libraries={isAdmin ? allLibraries : publicLibraries}
          userId={user!.id}
          loading={loading}
          emptyText={isAdmin ? 'No libraries yet.' : 'No public libraries yet.'}
          onPageChange={(page) => loadLibraries(isAdmin ? undefined : 1, page)}
          onSelect={(id) => navigate(`/library/${id}`)}
        />
      </section>

      <CreateLibraryModal
        open={createOpen}
        loading={creating}
        onCancel={() => setCreateOpen(false)}
        onSubmit={handleCreate}
      />
    </Space>
  );
};
