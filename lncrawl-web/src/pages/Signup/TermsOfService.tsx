import { Button, Modal, Typography } from 'antd';
import { useState } from 'react';
import './policy-content.scss';

export const TermsOfService: React.FC<any> = () => {
  const [error, setError] = useState<string>();
  const [termsModalOpen, setTermsModalOpen] = useState<boolean>(false);
  const [termsContent, setTermsContent] = useState<string>('');
  const [loadingTerms, setLoadingTerms] = useState<boolean>(false);

  const loadTermsOfService = async () => {
    if (termsContent) {
      setTermsModalOpen(true);
      return;
    }
    setLoadingTerms(true);
    try {
      const response = await fetch('/TERMS_OF_SERVICE.html');
      if (!response.ok) {
        throw new Error(`Failed to load: ${response.statusText}`);
      }
      const html = await response.text();
      setTermsContent(html);
      setTermsModalOpen(true);
    } catch (err) {
      setError('Failed to load terms of service. Please try again later.');
      console.error('Error loading terms of service:', err);
    } finally {
      setLoadingTerms(false);
    }
  };

  return (
    <>
      <Typography.Link
        onClick={(e) => {
          e.preventDefault();
          loadTermsOfService();
        }}
        style={{ padding: 0 }}
      >
        Terms of Service
      </Typography.Link>

      <Modal
        title="Terms of Service"
        open={termsModalOpen}
        onCancel={() => setTermsModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setTermsModalOpen(false)}>
            Close
          </Button>,
        ]}
        width={800}
        style={{ top: 20 }}
      >
        <div
          style={{
            maxHeight: '70vh',
            overflowY: 'auto',
            padding: '16px 0',
          }}
        >
          {loadingTerms ? (
            <Typography.Text>Loading...</Typography.Text>
          ) : error ? (
            <Typography.Text type="danger">{error}</Typography.Text>
          ) : (
            <div
              className="policy-content"
              dangerouslySetInnerHTML={{ __html: termsContent }}
              style={{
                lineHeight: '1.6',
              }}
            />
          )}
        </div>
      </Modal>
    </>
  );
};
