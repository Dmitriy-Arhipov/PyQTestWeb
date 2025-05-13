# delete-методы по спецключу для отладки и тестов: secret_key='PyQTest_secret_key'
# def delete(self, **kwargs):
#     global session
#     abort_if_not_found(kwargs['id'], Works, 'Test')
#     if hash(kwargs['secret_key']) != -1823148876541197958:
#         return jsonify({'result': 'No permission'})
#     works = session.query(Works).get(kwargs['id'])
#     session.delete(works)
#     session.commit()
#     return jsonify({'result': 'OK'})
# def delete(self, **kwargs):
#     global session
#     abort_if_not_found(kwargs['id'], TestAsks, 'Ask')
#     asks = session.query(TestAsks).get(kwargs['id'])
#     session.delete(asks)
#     session.commit()
#     return jsonify({'success': 'OK'})
# def delete(self, **kwargs):
#     global session
#     abort_if_not_found(kwargs['id'], Answers, 'Test')
#     if hash(kwargs['secret_key']) != -1823148876541197958:
#         return jsonify({'result': 'No permission'})
#     ans = session.query(Answers).get(kwargs['id'])
#     session.delete(ans)
#     session.commit()
#     return jsonify({'result': 'OK'})
